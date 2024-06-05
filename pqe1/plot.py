import altair as alt
import pandas as pd

df = pd.read_csv("res.tsv", sep="\t").\
groupby(["ud", "ui"])["winner"].\
value_counts(dropna=False).\
to_frame().\
reset_index(drop=False).\
sort_values(by=["ud", "ui", "winner"])

print(df)
