#!/usr/bin/env python3
"""
Variable-rate flash logging: storage savings vs. depth-error accuracy.

Goal of the flash-log rate algorithm (DiffAimdRateAlgorithm):
  1. Minimise stored log points (save flash space)
  2. Keep the signed depth error between logged and true profile small —
     both average error (accuracy) and maximum error (worst case)

Fixed-rate logging stores far more points and, crucially, allows large
transient errors (up to ~5.8 m at 90 m) because a constant interval
misses rapid depth changes.  The variable-rate algorithm adapts the
interval to the rate of depth change, compressing the log ~3.6–4.1×
while capping the maximum error below 70 cm.

The right column uses two stacked sub-panels so the max error (metres)
and the avg/median error (centimetres) are both readable on their own
scales.  Median is 0.000 m for all configurations.

Data source: flash_profile_diff_summary.csv from
             STDC-STM32-rs/results/newest/*.tables
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker

PROFILES = ["20 m", "50 m", "90 m"]

LOG_POINTS = {
    "Baseline fixed":     [ 78, 332, 599],
    "Exponential":        [ 19,  85, 152],
    "Linear-exponential": [ 20,  90, 149],
}

# Maximum absolute depth error [m]
MAX_ABS_ERROR = {
    "Baseline fixed":     [0.009, 3.067, 5.812],
    "Exponential":        [0.000, 0.358, 0.700],
    "Linear-exponential": [0.026, 0.420, 0.671],
}

# Average absolute depth error [m]  (|avg signed error| from table)
AVG_ABS_ERROR = {
    "Baseline fixed":     [0.000, 0.025, 0.022],
    "Exponential":        [0.000, 0.004, 0.007],
    "Linear-exponential": [0.001, 0.005, 0.004],
}

# Median depth error [m] — 0.000 for all configurations
MEDIAN_ERROR = {
    "Baseline fixed":     [0.000, 0.000, 0.000],
    "Exponential":        [0.000, 0.000, 0.000],
    "Linear-exponential": [0.000, 0.000, 0.000],
}

C_FIXED = "#57606a"
C_EXP   = "#1f6feb"
C_THAL  = "#d1242f"
COLORS  = [C_FIXED, C_EXP, C_THAL]
HATCHES = ["", "//", ".."]

x = np.arange(len(PROFILES))
width = 0.25
keys = list(LOG_POINTS.keys())

# Layout: left column (log points, full height) + right column (2 stacked rows)
fig = plt.figure(figsize=(10.5, 6.4))
gs = gridspec.GridSpec(2, 2, figure=fig,
                       height_ratios=[1.15, 1],
                       hspace=0.55, wspace=0.32)
ax1  = fig.add_subplot(gs[:, 0])   # left column, full height
ax2t = fig.add_subplot(gs[0, 1])   # right top — max error
ax2b = fig.add_subplot(gs[1, 1])   # right bottom — avg & median error

# ── left panel: log points stored ──────────────────────────────────────────
for i, (key, color, hatch) in enumerate(zip(keys, COLORS, HATCHES)):
    vals = LOG_POINTS[key]
    bars = ax1.bar(x + (i - 1) * width, vals, width,
                   label=key, color=color, alpha=0.88,
                   hatch=hatch, edgecolor="white", linewidth=0.5)
    for bar, v in zip(bars, vals):
        ax1.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 4,
                 str(v), ha="center", va="bottom",
                 fontsize=8.5, color=color)

fixed_pts = LOG_POINTS["Baseline fixed"]
for algo_i, key in enumerate(keys[1:], start=1):
    for j, (base, var) in enumerate(zip(fixed_pts, LOG_POINTS[key])):
        if base > 0 and var > 0:
            ax1.text(x[j] + (algo_i - 1) * width,
                     LOG_POINTS[key][j] / 2,
                     f"÷{base/var:.1f}×",
                     ha="center", va="center",
                     fontsize=7.5, color="white", fontweight="bold")

ax1.set_xticks(x)
ax1.set_xticklabels(PROFILES)
ax1.set_xlabel("Dive profile")
ax1.set_ylabel("Flash log points stored")
ax1.set_title("Log points stored", fontsize=11)
ax1.legend(fontsize=8.5, framealpha=0.95)
ax1.grid(axis="y", alpha=0.22)
ax1.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

# ── right top: max absolute error ──────────────────────────────────────────
for i, (key, color, hatch) in enumerate(zip(keys, COLORS, HATCHES)):
    vals_cm = [v * 100 for v in MAX_ABS_ERROR[key]]
    bars = ax2t.bar(x + (i - 1) * width, vals_cm, width,
                    color=color, alpha=0.88, hatch=hatch,
                    edgecolor="white", linewidth=0.5)
    for bar, v in zip(bars, vals_cm):
        if v >= 0.1:
            ax2t.text(bar.get_x() + bar.get_width() / 2,
                      bar.get_height() + 2,
                      f"{v:.0f}", ha="center", va="bottom",
                      fontsize=7.5, color=color, fontweight="bold")

ax2t.axhline(70, color="#8250df", ls="-.", lw=1.2, zorder=3)
ax2t.text(x[-1] + width * 1.1, 72, "70 cm",
          ha="left", va="bottom", fontsize=8, color="#8250df")

ax2t.set_xticks(x)
ax2t.set_xticklabels(PROFILES)
ax2t.set_ylabel("Max error  [cm]")
ax2t.set_title("Maximum depth error", fontsize=11)
ax2t.grid(axis="y", alpha=0.22)
ax2t.set_ylim(0, max(v * 100 for vals in MAX_ABS_ERROR.values() for v in vals) * 1.18)

# ── right bottom: avg & median error ───────────────────────────────────────
# Convert to cm for readability
for i, (key, color, hatch) in enumerate(zip(keys, COLORS, HATCHES)):
    avg_cm = [v * 100 for v in AVG_ABS_ERROR[key]]
    bx = x + (i - 1) * width
    bars = ax2b.bar(bx, avg_cm, width,
                    label=key, color=color, alpha=0.88, hatch=hatch,
                    edgecolor="white", linewidth=0.5)
    for bar, v in zip(bars, avg_cm):
        if v >= 0.05:
            ax2b.text(bar.get_x() + bar.get_width() / 2,
                      bar.get_height() + 0.03,
                      f"{v:.1f}", ha="center", va="bottom",
                      fontsize=7.5, color=color)

ax2b.set_xticks(x)
ax2b.set_xticklabels(PROFILES)
ax2b.set_xlabel("Dive profile")
ax2b.set_ylabel("Avg error  [cm]")
ax2b.set_title("Average depth error", fontsize=11)
ax2b.legend(fontsize=7.5, framealpha=0.95)
ax2b.grid(axis="y", alpha=0.22)
ax2b.set_ylim(0, max(v * 100 for vals in AVG_ABS_ERROR.values() for v in vals) * 1.22)

fig.suptitle(
    "Variable-rate flash logging: storage savings and depth accuracy\n"
    "White labels show compression ratio vs. fixed-rate baseline",
    fontsize=12.5,
)

out = "fig_flash_rate.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"Figure written: {out}")
