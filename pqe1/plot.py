import altair as alt
import glob
import numpy as np
import pandas as pd

df = pd.read_csv("res.tsv", sep="\t").\
groupby(["ud", "ui"])["winner"].\
value_counts(dropna=False).\
to_frame().\
reset_index(drop=False).\
pivot(
    columns="winner",
    index=["ud", "ui"],
    values="count",
).\
reset_index(drop=False).\
sort_values(by=["ud", "ui"]).\
fillna(0)

df.columns = df.columns.fillna("no_mut")
df = df.assign(
    no_mut=df.no_mut / 100,
    d=df.d / 100,
    i=df.i / 100,
    rel_i=df.i / (df.i + df.d),
)

df = df.assign(mut=1 - df.no_mut)

mut_freq = alt.Chart(df).mark_rect().encode(
    x=alt.X(
        "ui:O",
        sort="ascending",
        axis=alt.Axis(
            formatType="number",
            format=".2e",
            title="\u03bc_i",
        ),
    ),
    y=alt.Y(
        "ud:O",
        sort="descending",
        axis=alt.Axis(
            formatType="number",
            format=".2e",
            title="\u03bc_d",
        ),
    ),
    color=alt.Color(
        "mut",
        scale=alt.Scale(
            scheme="blues",
        ),
        legend=alt.Legend(
            title="Freq",
        ),
    ),
).properties(
    title="Frequency of any resistance mutation before t = 10,000 hours",
)

mut_freq.save("charts/mut_freq.html")

type_freq = alt.Chart(df).mark_rect().encode(
    x=alt.X(
        "ui:O",
        sort="ascending",
        axis=alt.Axis(
            formatType="number",
            format=".2e",
            title="\u03bc_i",
        ),
    ),
    y=alt.Y(
        "ud:O",
        sort="descending",
        axis=alt.Axis(
            formatType="number",
            format=".2e",
            title="\u03bc_d",
        ),
    ),
    color=alt.Color(
        "rel_i",
        scale=alt.Scale(
            scheme="redblue",
            reverse=True,
        ),
        legend=alt.Legend(
            title="Prop",
        ),
    ),
).properties(
    title="Proportion of resistance mutations that were replication-independent",
)

nulls = type_freq.transform_filter(
  "!isValid(datum.rel_i)"
).mark_rect(opacity=0.75).encode(
    alt.Color(
        'rel_i:N',
        scale=alt.Scale(scheme='greys'),
        legend=alt.Legend(
            title="a" * 10,
            titleColor="white",
        ),
    ),
)

type_freq = alt.layer(type_freq, nulls)

type_freq.save("charts/type_freq.html")

traj = pd.read_csv("sel_trajs/1000.tsv", sep="\t")

trajplot = alt.Chart(traj).mark_line().encode(
    x="t:Q",
    y="N:Q",
).properties(
    width=500,
    title=[
        "Example growth trajectory",
        "\u03bc_d = 1e-05, \u03bc_i = 1e-10",
        "Acquired replication-dependent mutation at 6,885 h",
    ],
)

trajplot.save(f"charts/1000.html")
