#!/usr/bin/env python3
"""
Decompression schedule computation time — full distribution at 90 m.

Shows why median and average diverge: the cost is discretised into
"tiers" matching the number of active decompression stops.  Both
algorithms share the same worst-case ceiling (~55 ms) but the
linear-exponential algorithm has more samples in the 16 ms tier,
pushing its median up compared to the exponential algorithm.

Raw cycle counts extracted from STM32L476 DWT benchmarks (16 MHz clock).
Data source: STDC-STM32-rs/results/newest/*.clean.log
"""

import statistics
import numpy as np
import matplotlib.pyplot as plt

# Raw computation times in ms for the 90 m profile only.
LIN_EXP_90 = (
    [6.3451]*15 +
    [9.202,9.202,9.2016,9.2016,9.2016,9.2016,9.2016,
     9.0499,9.0499,9.0499,9.0499,9.0499,
     16.3326,16.3326,16.3325,16.3321,16.3321,16.3326,16.3326,
     16.0129,16.0133,16.0134,16.0134,16.0134,16.0134,16.0129,16.0129,
     30.1401,30.1401,30.1397,30.1401,
     43.1929,43.1934,43.1921,43.2282,
     49.2606,49.2606,49.1467,49.1467,
     55.1476,55.1476,55.1545,55.1607,55.1602,55.3193,55.3402,55.3414,
     49.4471,49.4471,30.326,30.3264,
     16.6335,16.4912,16.4912,16.4698,
     9.2968,9.3523,9.3087,9.3087,9.3087,9.3083,9.3087,
     9.4509,9.4504,9.2581,9.2581,9.2577,9.2342,9.2342,9.2342]
)

EXP_90 = (
    [6.3468]*20 +
    [9.2011,9.2009,9.2009,9.2011,9.2011,9.2011,9.2011,9.2007,
     9.0491,9.0491,9.0491,
     16.3343,16.3343,16.3346,16.3343,16.3342,16.3343,
     16.0144,16.0144,16.0144,16.0143,16.0144,16.0144,16.0144,
     30.1304,30.1301,30.1463,30.1461,
     36.6759,36.6894,
     43.2027,43.2021,43.2026,
     49.2728,49.2729,49.2663,
     55.1519,55.1751,55.3335,55.3336,55.3554,55.3558,
     55.3551,55.3551,55.3551,55.3561,55.3561,55.3558,
     49.4594,49.4594,49.4591,43.4497,23.7109,16.4937,
     9.2963,9.3518,9.3518,9.3518,9.3518,9.3518,9.3518,
     9.3515,9.3519,9.3519,9.3519,9.3081,
     9.4504,9.4504,9.4329,9.2575,9.2402,9.2402]
)

C_EXP  = "#1f6feb"
C_THAL = "#d1242f"

fig, axes = plt.subplots(1, 2, figsize=(10.5, 6.4), sharey=False)

# --- left: strip / dot plot (all individual samples, jittered) ---
ax = axes[0]
rng = np.random.default_rng(42)

def jitter(n, width=0.18):
    return rng.uniform(-width, width, n)

y_thal = np.array(sorted(LIN_EXP_90))
y_exp  = np.array(sorted(EXP_90))

ax.scatter(1 + jitter(len(y_thal)), y_thal, color=C_THAL, alpha=0.55,
           s=22, label="Linear-exponential")
ax.scatter(2 + jitter(len(y_exp)),  y_exp,  color=C_EXP,  alpha=0.55,
           s=22, label="Exponential")

for yvals, xpos, col in [(y_thal, 1, C_THAL), (y_exp, 2, C_EXP)]:
    med = statistics.median(yvals)
    avg = statistics.mean(yvals)
    ax.hlines(med, xpos - 0.28, xpos + 0.28, colors=col, lw=2.2, zorder=5)
    ax.hlines(avg, xpos - 0.22, xpos + 0.22, colors=col, lw=1.4,
              linestyles="--", zorder=5)

# phantom lines for legend
ax.plot([], [], color="#444", lw=2.2, label="median")
ax.plot([], [], color="#444", lw=1.4, ls="--", label="mean")

ax.set_xticks([1, 2])
ax.set_xticklabels(["Linear-exp.", "Exponential"])
ax.set_xlim(0.5, 2.5)
ax.set_ylabel("Computation time  [ms]")
ax.set_title("All samples — 90 m profile", fontsize=11.5)
ax.legend(fontsize=9, framealpha=0.95)
ax.grid(axis="y", alpha=0.22)

# --- right: histogram (stacked, side-by-side bins) ---
ax2 = axes[1]
bins = np.arange(0, 62, 2)
ax2.hist(y_thal, bins=bins, color=C_THAL, alpha=0.75, label="Linear-exponential",
         edgecolor="white", lw=0.4)
ax2.hist(y_exp, bins=bins, color=C_EXP, alpha=0.75, label="Exponential",
         edgecolor="white", lw=0.4)

for yvals, col in [(y_thal, C_THAL), (y_exp, C_EXP)]:
    ax2.axvline(statistics.median(yvals), color=col, lw=2.0, ls="-")
    ax2.axvline(statistics.mean(yvals),   color=col, lw=1.4, ls="--")

ax2.plot([], [], color="#444", lw=2.0, label="median")
ax2.plot([], [], color="#444", lw=1.4, ls="--", label="mean")

ax2.set_xlabel("Computation time  [ms]")
ax2.set_ylabel("Sample count")
ax2.set_title("Histogram — 90 m profile", fontsize=11.5)
ax2.legend(fontsize=9, framealpha=0.95)
ax2.grid(axis="y", alpha=0.22)

fig.suptitle("Decompression schedule computation time — 90 m dive (10 min)\n"
             "STM32L476 @ 16 MHz, DWT cycle benchmarks  |  "
             f"n={len(LIN_EXP_90)} lin-exp, n={len(EXP_90)} exp",
             fontsize=12.5)
fig.tight_layout()

out = "fig_timing_distribution.png"
fig.savefig(out, dpi=150)
print(f"Figure written: {out}")
