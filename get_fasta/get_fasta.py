import datetime
import gzip
import io
import polars as pl
import requests
import sys

"""
python get_fasta.py PROTEOME_ID SPECIES_TAXON_ID
"""

# Functions for reading and writing FASTA to and from Polars dataframes

def fold(text, chunk_length):
	"""
	Adds newlines to a string after every `chunk_length` characters.
	"""

	lines = []
	offset = 0
	while offset < len(text):
		lines.append(text[offset:offset + chunk_length])
		offset += chunk_length

	return "\n".join(lines)

def read_fasta(url):
	"""
	Downloads a FASTA from `url` and reads it into a Polars dataframe. Assumes the data is gzipped.
	"""

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
	"""
	Takes a Polars dataframe where one column is FASTA headers and the other column is the corresponding sequences, and
	writes it to `path` with newlines inserted into the sequences after every 60 characters.
	"""

	if df.columns != ["header", "seq"]:
		raise ValueError(f"df columns invalid: {df.columns}")

	with open(path, "w") as fasta_file:
		for i in range(df.shape[0]):
			fasta_file.write(f">{df.get_column('header')[i]}\n{fold(df.get_column('seq')[i], 60)}\n")

# Read in command line arguments
proteome_id = sys.argv[1]
species_id = sys.argv[2]

# Define URLs for FASTAs from Uniprot

# This URL provides the latest reference proteome from Uniprot for the species, which does not include isoforms
canonical_url = f"https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/reference_proteomes/Eukaryota/{proteome_id}/{proteome_id}_{species_id}.fasta.gz"

# This URL provides the small number of reviewed proteins for the species that are not included in the reference
# proteome. For example, for humans this is mostly immunoglobulin proteins and that kind of thing.
additional_url = f"https://rest.uniprot.org/uniprotkb/stream?compressed=true&format=fasta&includeIsoform=true&query=%28%28organism_id%3A{species_id}%29+AND+%28reviewed%3Atrue%29+NOT+%28proteome%3A{proteome_id}%29%29"

# This URL provides isoforms for the proteins in the reference proteome, as well as additional unreviewed proteins from
# TrEMBL.
isoforms_url = f"https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/reference_proteomes/Eukaryota/{proteome_id}/{proteome_id}_{species_id}_additional.fasta.gz"

prots = (
	
	# Read in the FASTA files
	pl.concat([
		read_fasta(canonical_url).with_columns(file_order=pl.lit(0)),
		read_fasta(additional_url).with_columns(file_order=pl.lit(1)),
		read_fasta(isoforms_url).with_columns(file_order=pl.lit(2)),
	])

	# Extract columns for joining and sorting
	.with_columns(
		database=pl.col("header").str.split("|").list.first(),
		seq_len=pl.col("seq").str.len_chars(),
		isoform_order=pl.when(pl.col("header").str.contains("Isoform")).then(1).otherwise(0),

		# Isoforms that are not in separate entries have no existence score. We want to de-prioritize isoforms anyways,
		# so when there's an entry where the existence score is null, we'll assign it a rank of 6 (existing scores are
		# 1 to 5)
		existence_rank=pl.col("header").str.extract(r"\ PE=(\d) ").fill_null("6"),

		# We're going to assign a column of random numbers, but always with the same seed, for consistent tie-breaking
		# when we sort
		tie_breaker=pl.int_range(pl.len()).sample(pl.len(), with_replacement=False, shuffle=True, seed=0),
	)

	# Sorting
	# First criterion: Reference proteome, then additional proteins, then isoforms
	# Within those groups: SwissProt database before TrEMBL database
	# Within that: Higher existence rank before lower existence rank
	# Within that: Non-isoforms before isoforms
	# Within that: Longer before shorter
	# Within that: Order by random rank column always generated with same seed, for consistent tie-breaking
	.sort(
		"file_order", "database", "existence_rank", "isoform_order", "seq_len", "tie_breaker",
		descending=[False, False, False, False, True, False]
	)

	# Select just the columns we need for saving, now that we've sorted everything
	.select("header", "seq")
)

save_fasta(prots, f"{datetime.datetime.today().strftime('%Y-%m-%d')}_Uniprot_{proteome_id}_{species_id}_sorted.fasta")
