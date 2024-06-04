import pandas as pd
import numpy as np
import scipy.stats
import sys

i_perm = int(sys.argv[1])
rng = np.random.default_rng(i_perm)

def sample_exp(r):
    return np.where(r == 0, np.inf, rng.exponential(scale=1 / r))

def simulate(i_perm, rate_eqs, deltas, N0, watch, winners, t_stop=10000):

    dist_filename = f"dists/{i_perm}.tsv"
    with open(dist_filename, "w") as dist_handle:
        dist_handle.write("\t".join(["t", "N"]) + "\n")

    t = 0
    N = N0
    winner = ""

    i = 0
    ostr = ""

    while True:

        ostr += "\t".join([str(t), str(N)]) + "\n"

        if i % 1000000 == 0:
            with open(dist_filename, "a") as dist_handle:
                dist_handle.write(ostr)
            ostr = ""

        if winner != "":
            break

        rates = []
        for rate_eq in rate_eqs:
            rates.append(rate_eq(N))

        rates = np.array(rates)
        times = sample_exp(rates)
        win_idx = np.argmin(times)

        if t + times[win_idx] >= t_stop:
            break

        t += times[win_idx]
        N += deltas[win_idx]

        if win_idx in watch:
            winner = winners[watch.index(win_idx)]

        i += 1


    if ostr != "":
        with open(dist_filename, "a") as dist_handle:
            dist_handle.write(ostr)

    return t, N, winner

umin_exp = -10
umax_exp = -1

us = np.logspace(
    umin_exp,
    umax_exp,
    num=2 * (abs(umin_exp - umax_exp) + 1) - 1,
    base=10,
)

combus = np.dstack(np.meshgrid(us, us)).reshape(-1, 2)
combus = pd.DataFrame(combus, columns=["ud", "ui"])

i_u = i_perm // 100
ud = combus.loc[i_u, "ud"]
ui = combus.loc[i_u, "ui"]

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
    d=0.97,
    ud=ud,
    ui=ui,
)

t, N, winner = simulate(
    i_perm=i_perm,
    rate_eqs=list(terms.keys()),
    deltas=list(terms.values()),
    N0=150,
    watch=[2, 3],
    winners=["d", "i"],
)


with open(f"out/{i_perm}.out", "w") as handle:
    handle.write("\t".join([
        str(i_perm),
        str(ud),
        str(ui),
        str(t),
        str(N),
        winner,
    ]) + "\n")
