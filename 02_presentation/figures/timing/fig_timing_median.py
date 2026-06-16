#!/usr/bin/env python3
"""
Decompression schedule computation time — median per dive profile.

Two algorithms compared:
  * Exponential        (pure exponential, Bühlmann-like)
  * Linear-exponential (Thalmann: linear while supersaturated, then exponential)

Raw cycle counts extracted from STM32L476 DWT benchmarks (16 MHz clock).
Data source: STDC-STM32-rs/results/newest/*.clean.log
"""

import statistics
import numpy as np
import matplotlib.pyplot as plt

CLOCK_HZ = 16_000_000

# Raw DWT cycle counts → ms (cycles / CLOCK_HZ * 1000), extracted from logs.
RAW = {
    "Linear-exponential": {
        "20m": [6.335]*9,
        "50m": [6.3452]*29 + [8.5273,8.5273,8.5342,8.5342,8.5342,8.5342,8.5342,
                8.2784,8.2784,8.3924,8.3923,8.3923,8.3923,8.3919,8.3919,8.3919,8.3987,
                15.238,15.2384,15.2384,15.2384,15.238,15.2453,15.2444,
                21.8006,21.8006,21.8007,21.8007,21.8161,21.8161,21.8161,
                21.8152,21.8152,21.8152,21.8157,21.8157,21.8162,21.8162,21.8166,
                15.2667,15.2672,8.4356,8.4356,8.4356,8.4356,8.5849,8.5849],
        "90m": [6.3451]*15 +
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
                9.4509,9.4504,9.2581,9.2581,9.2577,9.2342,9.2342,9.2342],
    },
    "Exponential": {
        "20m": [6.3411]*8,
        "50m": [6.3571]*31 +
               [8.543,8.5433,8.55,8.5503,8.5503,8.55,
                8.4013,8.4081,8.4081,8.4081,8.4081,8.4084,8.4084,8.4084,
                8.4083,8.4083,8.4083,8.4081,8.4081,8.4153,8.4367,
                15.2668,15.2668,15.2668,15.2668,15.2734,15.2736,15.2733,
                15.2733,15.2737,15.2733,15.2739,15.2733,
                21.8419,21.8418,21.8418,21.8414,21.8562,21.8562,21.8566,
                21.8566,21.8561,21.8561,21.8561,21.8566,21.8563,21.8562,21.8562,
                15.2951,15.2951,8.4515,8.4515,8.4446,
                8.6005,8.6003,8.6003,8.6006],
        "90m": [6.3468]*20 +
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
                9.4504,9.4504,9.4329,9.2575,9.2402,9.2402],
    },
}

PROFILES = ["20m", "50m", "90m"]
PROFILE_LABELS = ["20 m  (2 min)", "50 m  (15 min)", "90 m  (10 min)"]

C_EXP  = "#1f6feb"   # blue  — exponential
C_THAL = "#d1242f"   # red   — linear-exponential

medians = {algo: [statistics.median(RAW[algo][p]) for p in PROFILES]
           for algo in RAW}

x = np.arange(len(PROFILES))
width = 0.35

fig, ax = plt.subplots(figsize=(10.5, 6.4))

bars_thal = ax.bar(x - width/2, medians["Linear-exponential"], width,
                   label="Linear-exponential (Thalmann)", color=C_THAL, alpha=0.88)
bars_exp  = ax.bar(x + width/2, medians["Exponential"], width,
                   label="Exponential (Bühlmann-like)", color=C_EXP, alpha=0.88)

for bar in bars_thal:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
            f"{bar.get_height():.1f}", ha="center", va="bottom", fontsize=9.5, color=C_THAL)
for bar in bars_exp:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
            f"{bar.get_height():.1f}", ha="center", va="bottom", fontsize=9.5, color=C_EXP)

ax.set_xticks(x)
ax.set_xticklabels(PROFILE_LABELS)
ax.set_xlabel("Dive profile")
ax.set_ylabel("Median computation time  [ms]")
ax.set_title("Decompression schedule computation time — median per profile\n"
             "STM32L476 @ 16 MHz, DWT cycle benchmarks",
             fontsize=12.5)
ax.legend(loc="upper left", framealpha=0.95)
ax.set_ylim(0, max(max(medians["Linear-exponential"]), max(medians["Exponential"])) * 1.22)
ax.grid(axis="y", alpha=0.25)
fig.tight_layout()

out = "fig_timing_median.png"
fig.savefig(out, dpi=150)
print(f"Figure written: {out}")
