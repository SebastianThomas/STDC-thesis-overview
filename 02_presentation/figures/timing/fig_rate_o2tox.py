#!/usr/bin/env python3
"""
Variable-rate scheduling effect on the O2-toxicity algorithm.

Left panel  — execution count: how many times O2Tox is actually run
              under fixed-rate vs. variable-rate scheduling.
Right panel — per-call cost (µs): O2Tox algorithm vs. rate-check overhead.
              Unlike deco, the O2Tox algorithm itself is only ~16.6 µs,
              so the variable-rate check (~115 µs) costs ~7× MORE per call
              than the algorithm it guards — making the execution-count
              reduction (left panel) even more critical.

O2Tox cost is constant across all profiles (single measurement, no
profile-dependent branching), so the right panel shows per-config averages.

Data source: summary.csv from STDC-STM32-rs/results/newest/*.tables
             (cycles converted to µs at 16 MHz STM32L476)
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches

PROFILES = ["20 m", "50 m", "90 m"]

# ── execution counts ───────────────────────────────────────────────────────
O2TOX_COUNTS = {
    "Baseline fixed":     [ 8,  42,  87],
    "Exponential":        [ 1,  27,  26],
    "Linear-exponential": [ 1,  34,  27],
}

# ── per-call avg cost in µs (constant across profiles) ────────────────────
# Values averaged over profiles for display; variation is < 0.5 µs
ALGO_US = {
    "Baseline fixed":     16.6,
    "Exponential":        16.6,
    "Linear-exponential": 16.6,
}
RATE_US = {
    "Baseline fixed":     14.7,
    "Exponential":        116.0,
    "Linear-exponential": 115.6,
}

C_FIXED = "#57606a"
C_EXP   = "#1f6feb"
C_THAL  = "#d1242f"
COLORS  = [C_FIXED, C_EXP, C_THAL]
HATCHES = ["", "//", ".."]

x     = np.arange(len(PROFILES))
width = 0.25
keys  = list(O2TOX_COUNTS.keys())

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 6.4))

# ── left: execution count ──────────────────────────────────────────────────
for i, (key, color, hatch) in enumerate(zip(keys, COLORS, HATCHES)):
    vals = O2TOX_COUNTS[key]
    bars = ax1.bar(x + (i - 1) * width, vals, width,
                   label=key, color=color, alpha=0.88,
                   hatch=hatch, edgecolor="white", linewidth=0.5)
    for bar, v in zip(bars, vals):
        ax1.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 0.5,
                 str(v), ha="center", va="bottom",
                 fontsize=9.5, color=color)

fixed = O2TOX_COUNTS["Baseline fixed"]
for algo_i, key in enumerate(keys[1:], start=1):
    for j, (base, var) in enumerate(zip(fixed, O2TOX_COUNTS[key])):
        if base > 0 and var > 0:
            ax1.text(x[j] + (algo_i - 1) * width,
                     O2TOX_COUNTS[key][j] / 2,
                     f"÷{base/var:.1f}×",
                     ha="center", va="center",
                     fontsize=8, color="white", fontweight="bold")
        elif base > 0 and var == 0:
            ax1.text(x[j] + (algo_i - 1) * width, 0.4,
                     "zero", ha="center", va="bottom",
                     fontsize=7.5, color=COLORS[algo_i])

ax1.set_xticks(x)
ax1.set_xticklabels(PROFILES)
ax1.set_xlabel("Dive profile")
ax1.set_ylabel("Algorithm executions")
ax1.set_title("Execution count per profile", fontsize=11.5)
ax1.legend(fontsize=9, framealpha=0.95)
ax1.grid(axis="y", alpha=0.22)
ax1.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
ax1.set_ylim(0, max(max(v) for v in O2TOX_COUNTS.values()) * 1.18)

# ── right: per-call cost (linear, µs) ─────────────────────────────────────
# O2Tox cost is constant across profiles — show per-config comparison.
xi = np.arange(len(keys))
w2 = 0.32

algo_vals = [ALGO_US[k] for k in keys]
rate_vals = [RATE_US[k] for k in keys]

for i, (key, color, hatch) in enumerate(zip(keys, COLORS, HATCHES)):
    ax2.bar(xi[i] - w2 / 2, algo_vals[i], w2,
            color=color, alpha=0.88, hatch=hatch,
            edgecolor="white", linewidth=0.5)
    ax2.bar(xi[i] + w2 / 2, rate_vals[i], w2,
            color=color, alpha=0.40,
            edgecolor=color, linewidth=1.0)
    ratio = RATE_US[key] / ALGO_US[key]   # rate / algo
    # value labels just above each bar (tight gap)
    ax2.text(xi[i] - w2 / 2, algo_vals[i] + 0.5,
             f"{algo_vals[i]:.1f}", ha="center", va="bottom",
             fontsize=9, color=color)
    ax2.text(xi[i] + w2 / 2, rate_vals[i] + 0.5,
             f"{rate_vals[i]:.1f}", ha="center", va="bottom",
             fontsize=9, color=color)
    # ÷N× label centred inside the shorter bar, horizontal
    if ratio > 1:
        ax2.text(xi[i] - w2 / 2, algo_vals[i] / 2,
                 f"÷{ratio:.1f}×", ha="center", va="center",
                 fontsize=8, color="white", fontweight="bold")
    else:
        ax2.text(xi[i] + w2 / 2, rate_vals[i] / 2,
                 f"÷{1/ratio:.1f}×", ha="center", va="center",
                 fontsize=8, color="white", fontweight="bold")

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

ax2.set_xticks(xi)
ax2.set_xticklabels(keys, fontsize=9)
ax2.set_xlabel("Configuration")
ax2.set_ylabel("Avg per-call cost  [µs]")
ax2.set_title("Per-call cost: algorithm vs. rate check", fontsize=11.5)
ax2.legend(handles=legend_handles, fontsize=8.5, framealpha=0.95, ncol=2)
ax2.grid(axis="y", alpha=0.22)
ax2.set_ylim(0, max(rate_vals) * 1.35)

fig.suptitle(
    "Variable-rate O₂-toxicity scheduling: execution count & per-call cost\n"
    "White labels (left) show reduction factor vs. fixed-rate baseline",
    fontsize=12.5,
)
fig.tight_layout()

out = "fig_rate_o2tox.png"
fig.savefig(out, dpi=150)
print(f"Figure written: {out}")
