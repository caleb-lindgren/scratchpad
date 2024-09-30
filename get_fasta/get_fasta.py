import datetime
import gzip
import io
import polars as pl
import requests
import sys

"""
python get_fasta.py PROTEOME_ID TAXON_ID
"""

# Functions for reading and writing FASTA to and from Polars dataframes

def fold(text, chunk_length):

	lines = []
	offset = 0
	while offset < len(text):
		lines.append(text[offset:offset + chunk_length])
		offset += chunk_length

	return "\n".join(lines)

def read_fasta(url):

	resp = requests.get(url)
	bytes = io.BytesIO(resp.content)
	with gzip.open(bytes, mode="rt") as handle:
		lines = handle.readlines()

	headers = []
	seqs = []

	curr = -1
	for line in lines:
		if line.startswith(">"):
			headers.append(line.strip()[1:])
			curr += 1
			seqs.append("")
		else:
			seqs[curr] += line.strip()

	df = pl.DataFrame({"header": headers, "seq": seqs})

	return df

def save_fasta(df, path):

	if df.columns != ["header", "seq"]:
		raise ValueError(f"df columns invalid: {df.columns}")

	with open(path, "w") as fasta_file:
		for i in range(df.shape[0]):
			fasta_file.write(f">{df.get_column('header')[i]}\n{fold(df.get_column('seq')[i], 60)}\n")

# Read in the FASTA files

proteome_id = sys.argv[1]
taxon_id = sys.argv[2]

canonical_url = f"https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/reference_proteomes/Eukaryota/{proteome_id}/{proteome_id}_{taxon_id}.fasta.gz"
additional_url = f"https://rest.uniprot.org/uniprotkb/stream?compressed=true&format=fasta&includeIsoform=true&query=%28%28organism_id%3A{taxon_id}%29+AND+%28reviewed%3Atrue%29+NOT+%28proteome%3A{proteome_id}%29%29"
isoforms_url = f"https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/reference_proteomes/Eukaryota/{proteome_id}/{proteome_id}_{taxon_id}_additional.fasta.gz"

prots = (
	pl.concat([
		read_fasta(canonical_url).with_columns(file_order=pl.lit(0)),
		read_fasta(additional_url).with_columns(file_order=pl.lit(1)),
		read_fasta(isoforms_url).with_columns(file_order=pl.lit(2)),
	])

	# Extract columns for joining and sorting
	.with_columns(
		pl.col("header").str.split("|").list.first().alias("db"),
		pl.col("seq").str.len_chars().alias("seq_len"),
		pl.when(pl.col("header").str.contains("Isoform")).then(1).otherwise(0).alias("isoform_order"),

		# Isoforms that are not in separate entries have no existence rank. We want to de-prioritize isoforms anyways,
		# so we'll assign them a new rank of 6
		pl.col("header").str.extract(r"\ PE=(\d) ").fill_null("6").alias("existence_rank"),
	)

	# Discard dubious sequences, see https://www.uniprot.org/help/dubious_sequences
	.filter(pl.col("existence_rank") != "5")

	# Sorting
	# First criterion: Reference proteome, then additional proteins, then isoforms
	# Within those groups: SwissProt before TrEMBL
	# Within that: Higher existence rank before lower existence rank
	# Within that: Non-isoforms before isoforms
	# Within that: Longer before shorter
	.sort("file_order", "db", "existence_rank", "isoform_order", "seq_len", descending=[False, False, False, False, True])

	# Select the columns for saving
	.select("header", "seq")
)

save_fasta(prots, f"{datetime.datetime.today().strftime('%Y-%m-%d')}_Uniprot_{proteome_id}_{taxon_id}_sorted.fasta")
