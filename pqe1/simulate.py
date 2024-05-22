import altair as alt
import pandas as pd
import numpy as np
import scipy.stats

rng = np.random.default_rng()

def sample_exp(r):
    return np.where(r == 0, np.inf, rng.exponential(scale=1 / r))

def simulate(rate_eqs, deltas, N0, watch, t_stop=1000):

    t = 0
    N = N0
    ts = []
    Ns = []

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
            print(f"N: {N}, t: {t}, idx: {win_idx}")

    res = pd.DataFrame({"t": ts, "N": Ns})

    return res

def plot_over_time(dist):

    chart = alt.Chart(dist).mark_line().encode(
        x="t",
        y="N",
    ).properties(
        height=200,
        width=400,
    )

    return chart

def plot_steady_state_dist(rprod, rdeg, x0=0, t_stop=100, nperms=1000):

    ends = []
    for i in range(nperms):
        dist = simulate(
            rprod=rprod,
            rdeg=rdeg,
            x0=x0,
            t_stop=t_stop,
        )

        ends.append(dist.x.iloc[-1])
        del dist

    df = pd.DataFrame({"x": ends})
    mean = np.mean(ends)
    std = np.std(ends)

    print(f"mean: {mean}")
    print(f"var: {std ** 2}")

    chart = alt.Chart(df).mark_bar().encode(
        x=alt.X(
            "x",
            bin=alt.Bin(step=3 * std // 10),
        ),
        y="count()",
    )

    return chart

if __name__ == "__main__":

    def make_terms():
        r = 0.0162
        d = 0.9259
        ud = 10e-7
        ui = 10e-4

        terms = {
            lambda N: N * r:       1,
            lambda N: N * r * d:  -1,
            lambda N: N * r * ud: -1,
            lambda N: ui:         -1,
        }

        return terms

    terms = make_terms()

    plot_over_time(simulate(
        rate_eqs=list(terms.keys()),
        deltas=list(terms.values()),
        N0=150,
        watch=[2, 3]
    )).save("out.html")
