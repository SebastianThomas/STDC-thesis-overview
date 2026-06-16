#!/usr/bin/env python3
"""
Variable-rate scheduling effect on the decompression schedule algorithm.

Left panel  — execution count: how many times deco is actually computed
              under fixed-rate vs. variable-rate scheduling.
Right panel — per-call cost (log scale, µs): decompression algorithm vs.
              rate-check overhead.  The rate check adds only 0.5–1.8% per
              call, so the net saving is nearly proportional to the
              execution-count reduction.

Data source: summary.csv from STDC-STM32-rs/results/newest/*.tables
             (cycles converted to µs at 16 MHz STM32L476)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches

CLOCK_HZ = 16_000_000
PROFILES  = ["20 m", "50 m", "90 m"]

# ── execution counts (samples column from timing_deco_schedule table) ──────
DECO_COUNTS = {
    "Baseline fixed":     [36,  137, 249],
    "Exponential":        [ 8,   88,  92],
    "Linear-exponential": [ 9,   76,  85],
}

# ── per-call avg cost in µs (avg_cycles / CLOCK_HZ * 1e6) ─────────────────
ALGO_US = {
    "Baseline fixed":     [6363, 11864, 23216],
    "Exponential":        [6341, 11090, 21448],
    "Linear-exponential": [6335, 11089, 20523],
}
RATE_US = {
    "Baseline fixed":     [13.7, 13.6, 13.8],
    "Exponential":        [113.2, 117.4, 114.9],
    "Linear-exponential": [112.6, 117.4, 114.6],
}

C_FIXED = "#57606a"
C_EXP   = "#1f6feb"
C_THAL  = "#d1242f"
COLORS  = [C_FIXED, C_EXP, C_THAL]
HATCHES = ["", "//", ".."]

x     = np.arange(len(PROFILES))
width = 0.25
keys  = list(DECO_COUNTS.keys())

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 6.4))

# ── left: execution count ──────────────────────────────────────────────────
for i, (key, color, hatch) in enumerate(zip(keys, COLORS, HATCHES)):
    vals = DECO_COUNTS[key]
    bars = ax1.bar(x + (i - 1) * width, vals, width,
                   label=key, color=color, alpha=0.88,
                   hatch=hatch, edgecolor="white", linewidth=0.5)
    for bar, v in zip(bars, vals):
        ax1.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 2,
                 str(v), ha="center", va="bottom",
                 fontsize=9.5, color=color)

fixed = DECO_COUNTS["Baseline fixed"]
for algo_i, key in enumerate(keys[1:], start=1):
    for j, (base, var) in enumerate(zip(fixed, DECO_COUNTS[key])):
        if base > 0 and var > 0:
            ax1.text(x[j] + (algo_i - 1) * width,
                     DECO_COUNTS[key][j] / 2,
                     f"÷{base/var:.1f}×",
                     ha="center", va="center",
                     fontsize=8, color="white", fontweight="bold")

ax1.set_xticks(x)
ax1.set_xticklabels(PROFILES)
ax1.set_xlabel("Dive profile")
ax1.set_ylabel("Algorithm executions")
ax1.set_title("Execution count per profile", fontsize=11.5)
ax1.legend(fontsize=9, framealpha=0.95)
ax1.grid(axis="y", alpha=0.22)
ax1.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
ax1.set_ylim(0, max(max(v) for v in DECO_COUNTS.values()) * 1.18)

# ── right: per-call cost at 50 m (log scale) ──────────────────────────────
# One representative profile; x-axis = configuration; two bars per config
# (algorithm solid, rate check light) with matching color + hatch.
xi  = np.arange(len(keys))
w2  = 0.32
P   = "50m"

algo_50 = [ALGO_US[k][1] for k in keys]   # index 1 = 50m
rate_50 = [RATE_US[k][1] for k in keys]

# Algorithm bars: hatched (solid fill + hatch), Rate check bars: no hatch, lighter alpha
for i, (key, color, hatch) in enumerate(zip(keys, COLORS, HATCHES)):
    ax2.bar(xi[i] - w2 / 2, algo_50[i], w2,
            color=color, alpha=0.88, hatch=hatch,
            edgecolor="white", linewidth=0.5)
    ax2.bar(xi[i] + w2 / 2, rate_50[i], w2,
            color=color, alpha=0.40,
            edgecolor=color, linewidth=1.0)
    # value labels just above each bar (tight gap on log scale: multiply by 1.05)
    ax2.text(xi[i] - w2 / 2, algo_50[i] * 1.05,
             f"{algo_50[i]:,.0f}", ha="center", va="bottom",
             fontsize=8.5, color=color)
    ax2.text(xi[i] + w2 / 2, rate_50[i] * 1.05,
             f"{rate_50[i]:.0f}", ha="center", va="bottom",
             fontsize=8.5, color=color)
    # ÷N× inside the rate check bar (always shorter for deco), horizontal
    ratio = algo_50[i] / rate_50[i]
    if rate_50[i] > 30:   # skip fixed-rate bar (too short on log scale)
        log_mid = (rate_50[i] ** 0.5) * 2.0
        ax2.text(xi[i] + w2 / 2, log_mid,
                 f"÷{ratio:.0f}×", ha="center", va="center",
                 fontsize=7.5, color="white", fontweight="bold")

# Legend via Patch for reliable colour rendering
legend_handles = [
    mpatches.Patch(facecolor=color, alpha=0.88, hatch=hatch,
                   edgecolor="white", label=key)
    for color, hatch, key in zip(COLORS, HATCHES, keys)
] + [
    mpatches.Patch(facecolor="#888", alpha=0.88, hatch="//",
                   edgecolor="white", label="Algorithm (hatched)"),
    mpatches.Patch(facecolor="#888", alpha=0.40,
                   edgecolor="#888", linewidth=1.0, label="Rate check (plain)"),
]

ax2.set_yscale("log")
ax2.set_xticks(xi)
ax2.set_xticklabels(keys, fontsize=9)
ax2.set_xlabel("Configuration  (50 m profile)")
ax2.set_ylabel("Avg per-call cost  [µs]  (log scale)")
ax2.set_title("Per-call cost: algorithm vs. rate check", fontsize=11.5)
ax2.legend(handles=legend_handles, fontsize=8.5, framealpha=0.95, ncol=2)
ax2.grid(axis="y", alpha=0.22, which="both")
ax2.yaxis.set_major_formatter(ticker.FuncFormatter(
    lambda v, _: f"{v:,.0f}" if v >= 1 else f"{v:.1f}"))

fig.suptitle(
    "Variable-rate deco scheduling: execution count & per-call cost\n"
    "White labels (left) show reduction factor vs. fixed-rate baseline",
    fontsize=12.5,
)
fig.tight_layout()

out = "fig_rate_deco.png"
fig.savefig(out, dpi=150)
print(f"Figure written: {out}")
