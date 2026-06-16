#!/usr/bin/env python3
"""
PCB Component Overview — Dive Computer presentation figures.

Produces two separate PNG files:
  fig_pcb_components.png  — star-topology diagram of PCB components
  fig_pcb_power.png       — horizontal power-consumption & battery-life chart

Power data (Section 5.1.1 of thesis):
  Surface mode:            18.5 mW  → 18.3 days
  Dive mode (display off): 35.0 mW  →  9.6 days
  Dive mode (display on): 545.0 mW  → 14.9 hours

Style matches existing timing/saturation figures:
  C_FIXED="#57606a", C_EXP="#1f6feb", C_THAL="#d1242f"
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

# ── colour palette (same as other figures) ────────────────────────────────────
C_GRAY  = "#57606a"   # MCU
C_BLUE  = "#1f6feb"   # SPI peripherals
C_RED   = "#d1242f"   # I2C peripheral (pressure sensor)
C_GREEN = "#2da44e"   # Battery

# ── font sizes (large for beamer) ────────────────────────────────────────────
FS_TITLE = 24
FS_COMP  = 20
FS_SUB   = 15
FS_AXIS  = 18
FS_TICK  = 16

# ═══════════════════════════════════════════════════════════════════════════════
# Figure 1 — PCB component diagram
# ═══════════════════════════════════════════════════════════════════════════════
fig1, ax = plt.subplots(figsize=(13, 6))
fig1.patch.set_facecolor("white")
ax.set_xlim(0, 13)
ax.set_ylim(4.2, 9.8)
ax.axis("off")


def draw_box(ax, cx, cy, w, h, label, sublabel, color,
             fs_comp=FS_COMP, fs_sub=FS_SUB):
    box = FancyBboxPatch(
        (cx - w / 2, cy - h / 2), w, h,
        boxstyle="round,pad=0.15",
        facecolor=color, edgecolor="white",
        linewidth=2.5, alpha=0.92, zorder=3, clip_on=False,
    )
    ax.add_patch(box)
    if sublabel:
        # multi-line main labels need more upward offset so sublabel has room
        n_lines = label.count("\n") + 1
        label_dy =  0.20 + 0.18 * (n_lines - 1)
        sub_dy   = -0.32 - 0.05 * (n_lines - 1)
        ax.text(cx, cy + label_dy, label, ha="center", va="center",
                fontsize=fs_comp, color="white", fontweight="bold",
                zorder=4, clip_on=False)
        ax.text(cx, cy + sub_dy, sublabel, ha="center", va="center",
                fontsize=fs_sub, color="white", alpha=0.90,
                zorder=4, clip_on=False)
    else:
        ax.text(cx, cy, label, ha="center", va="center",
                fontsize=fs_comp, color="white", fontweight="bold",
                zorder=4, clip_on=False)


def connector(ax, x1, y1, x2, y2, style="-"):
    ax.plot([x1, x2], [y1, y2], style, color="#999", lw=2.0, zorder=1)


# MCU shifted right — clears space for Battery + Power label on the left
MCU_X, MCU_Y = 8.5, 8.6
MCU_W, MCU_H = 5.5, 1.2
draw_box(ax, MCU_X, MCU_Y, MCU_W, MCU_H,
         "MCU  (STM32L476)", "Low-power · STOP2 mode", C_GRAY)

# 4 peripherals in a fan below MCU.
# Coordinate space is now 0–13, so BOX_W=2.8 fits comfortably.
BOX_W, BOX_H = 2.8, 1.3
FRAC1, FRAC2 = 0.12, 0.88
PERI_Y = 5.5

peripherals = [
    (1.8,  PERI_Y, "Pressure\nSensor",  "I²C  ·  0.1 – 30 bar", C_RED),
    (5.0,  PERI_Y, "Flash",             "SPI  ·  ≥ 100 dives",  C_BLUE),
    (8.6,  PERI_Y, "OLED Display",      "SPI  ·  1.8\"",        C_BLUE),
    (11.8, PERI_Y, "Bluetooth\nModule", "SPI",                   C_BLUE),
]

for cx, cy, label, sublabel, color in peripherals:
    draw_box(ax, cx, cy, BOX_W, BOX_H, label, sublabel, color,
             fs_comp=18, fs_sub=14)
    dx, dy = cx - MCU_X, cy - MCU_Y
    x1, y1 = MCU_X + dx * FRAC1, MCU_Y + dy * FRAC1
    x2, y2 = MCU_X + dx * FRAC2, MCU_Y + dy * FRAC2
    connector(ax, x1, y1, x2, y2)

# Battery: left of MCU at same height, dashed power line
BAT_X, BAT_Y = 1.8, 8.6
BAT_W, BAT_H = 2.8, 1.2
draw_box(ax, BAT_X, BAT_Y, BAT_W, BAT_H,
         "Battery", "2200 mAh  ·  3.7 V", C_GREEN)

BAT_RIGHT = BAT_X + BAT_W / 2 + 0.05
MCU_LEFT  = MCU_X - MCU_W / 2 - 0.05
connector(ax, BAT_RIGHT, BAT_Y, MCU_LEFT, MCU_Y, style="--")
ax.text((BAT_RIGHT + MCU_LEFT) / 2, BAT_Y - 0.20, "Power",
        ha="center", va="top", fontsize=FS_SUB, color="#666", style="italic",
        bbox=dict(facecolor="white", edgecolor="none", alpha=0.90, pad=2),
        zorder=5)

ax.set_title("PCB Components", fontsize=FS_TITLE, fontweight="bold", pad=4)

fig1.savefig("fig_pcb_components.png", dpi=150, bbox_inches="tight", facecolor="white")
print("Figure written: fig_pcb_components.png")
plt.close(fig1)

# ═══════════════════════════════════════════════════════════════════════════════
# Figure 2 — Power consumption & battery life
# ═══════════════════════════════════════════════════════════════════════════════
fig2, ax2 = plt.subplots(figsize=(8, 5))
fig2.patch.set_facecolor("white")

modes  = ["Dive mode\n(display on)", "Dive mode\n(display off)", "Surface\nmode"]
powers = [545.0, 35.0, 18.5]       # mW, high → low so surface is at top
batt   = ["14.9 hours", "9.6 days", "18.3 days"]
colors = [C_RED, C_BLUE, C_GREEN]

y = np.arange(len(modes))
ax2.barh(y, powers, 0.55, color=colors, alpha=0.88,
         edgecolor="white", linewidth=1.5)

for i, (pw, bt, c) in enumerate(zip(powers, batt, colors)):
    if pw > 100:
        ax2.text(pw / 2, i, f"→ {bt}", va="center", ha="center",
                 fontsize=FS_SUB, color="white", fontweight="bold")
        ax2.text(pw + 12, i, f"{pw:.0f} mW", va="center",
                 fontsize=FS_SUB, color=c, fontweight="bold")
    else:
        ax2.text(pw + 12, i + 0.20, f"{pw:.0f} mW", va="center",
                 fontsize=FS_SUB, color=c, fontweight="bold")
        ax2.text(pw + 12, i - 0.20, f"→ {bt}", va="center",
                 fontsize=FS_SUB - 1, color="#444")

ax2.set_yticks(y)
ax2.set_yticklabels(modes, fontsize=FS_AXIS)
ax2.set_xlabel("Power consumption [mW]", fontsize=FS_AXIS)
ax2.set_title("Power & Battery Life  (2200 mAh Li-Ion)",
              fontsize=FS_TITLE - 2, fontweight="bold")
ax2.tick_params(axis="x", labelsize=FS_TICK)
ax2.grid(axis="x", alpha=0.22)
ax2.set_xlim(0, 750)
ax2.spines["top"].set_visible(False)
ax2.spines["right"].set_visible(False)

fig2.tight_layout()
fig2.savefig("fig_pcb_power.png", dpi=150, bbox_inches="tight", facecolor="white")
print("Figure written: fig_pcb_power.png")
plt.close(fig2)
