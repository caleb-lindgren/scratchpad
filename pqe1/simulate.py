import altair as alt
import pandas as pd
import numpy as np
import scipy.stats
import sys

permi = sys.argv[1]
rng = np.random.default_rng(permi)

def sample_exp(r):
    return np.where(r == 0, np.inf, rng.exponential(scale=1 / r))

def simulate(rate_eqs, deltas, N0, watch, winners, t_stop=1000):

    t = 0
    N = N0
    ts = []
    Ns = []
    winner = None

    while True:

        if t >= t_stop:
            break

        ts.append(t)
        Ns.append(N)

        rates = []
        for rate_eq in rate_eqs:
            rates.append(rate_eq(N))

        rates = np.array(rates)
        times = sample_exp(rates)
        win_idx = np.argmin(times)
        t += times[win_idx]
        N += deltas[win_idx]

        if win_idx in watch:
            winner = winners[watch.index(win_idx)]
            break

    res = pd.DataFrame({"t": ts, "N": Ns})

    return res, winner

def plot_over_time(dist):

    chart = alt.Chart(dist).mark_line().encode(
        x="t",
        y="N",
    ).properties(
        height=200,
        width=400,
    )

    return chart

if __name__ == "__main__":

    us = pd.read_csv("us.tsv", sep="\t")
    ud = us.loc[permi, "ud"]
    ui = us.loc[permi, "ui"]

    def make_terms(r, d, ud, ui):

        terms = {
            lambda N: N * r:       1,
            lambda N: N * r * d:  -1,
            lambda N: N * r * ud: -1,
            lambda N: N * ui:     -1,
        }

        return terms

    terms = make_terms(
        r=0.0162,
        d=0.9259,
        ud=ud,
        ui=ui,
    )

    ks = []
    Nfs = []
    tfs = []
    for k in range(0, 10000):`

        dist, winner = simulate(
            rate_eqs=list(terms.keys()),
            deltas=list(terms.values()),
            N0=150,
            watch=[2, 3],
            winners=["d", "i"],
        )

        plot_over_time(dist).save(f"{permi}_{k}.html")