import altair as alt
import pandas as pd
import numpy as np
import scipy.stats

rng = np.random.default_rng()

def sample_exp(r):
    return np.inf if r == 0 else rng.exponential(scale=1 / r)

def simulate(rprod, rdeg, x0=0, t_stop=100):

    t = 0
    x = x0
    ts = []
    xs = []

    while True:

        if t >= t_stop:
            break

        ts.append(t)
        xs.append(x)

        rprod_x = rprod(x)
        rdeg_x = rdeg(x)

        t_prod = sample_exp(rprod_x)
        t_deg = sample_exp(rdeg_x)

        if t_prod < t_deg:
            t += t_prod
            x += 1
        else:
            t += t_deg
            x -= 1

    res = pd.DataFrame({"t": ts, "x": xs})

    return res

def make_rates_simple_constitutive(A, gamma):
    rates = {
        "rprod": lambda x: A,
        "rdeg": lambda x: gamma * x,
    }
    return rates

def make_rates_neg_autoregulation(B, K, gamma):
    rates = {
        "rprod": lambda x: B * K / (K + x),
        "rdeg": lambda x: gamma * x,
    }
    return rates

def plot_over_time(dist):

    chart = alt.Chart(dist).mark_line().encode(
        x="t",
        y="x",
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

    terms = {
        
    }

    plot_over_time(
        rates=terms.keys(),
        deltas=terms.values(),
    )

#    rates_A10 = make_rates_simple_constitutive(A=10, gamma=1)
#    rates_A100 = make_rates_simple_constitutive(A=100, gamma=1)
#
#    plot_over_time(simulate(rprod=rates_A10["rprod"], rdeg=rates_A10["rdeg"])).save("1d2iA10.html")
#    plot_over_time(simulate(rprod=rates_A100["rprod"], rdeg=rates_A100["rdeg"])).save("1d2Ai100.html")
#
#    plot_steady_state_dist(rprod=rates_A10["rprod"], rdeg=rates_A10["rdeg"]).save("1d2iiA10.html")
#    plot_steady_state_dist(rprod=rates_A100["rprod"], rdeg=rates_A100["rdeg"]).save("1d2Aii100.html")
#
#    rates_B = make_rates_neg_autoregulation(B=200, K=100, gamma=1)
#    plot_over_time(simulate(rprod=rates_B["rprod"], rdeg=rates_B["rdeg"])).save("1d3extra.html")
#    plot_steady_state_dist(rprod=rates_B["rprod"], rdeg=rates_B["rdeg"]).save("1d3.html")
