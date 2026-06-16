#!/usr/bin/env python3
"""
Desaturation of one compartment held at a fixed depth:
    * pure exponential   (Bühlmann-like)
    * Thalmann linear-then-exponential

A supersaturated compartment washes out on the SLOW LINEAR branch first, then
crosses to the exponential branch once its tension falls to the gas-phase
threshold, i.e. once

        total tissue gas tension  =  ambient pressure + PBOVP .

In single-inert-gas terms (total = inert tension + metabolic term PMET) that
crossover sits at an inert tension of   P_ambient + PBOVP - PMET .  The linear
slope equals the exponential slope evaluated at that crossover, so tension and
its derivative are continuous there.

Pressures in bar absolute.  Sea water: 10 m == 1 bar, surface == 1.0 bar.
"""

import numpy as np
import matplotlib.pyplot as plt

# --------------------------------------------------------------------------- #
P0, P_H2O, FN2 = 1.0, 0.0627, 0.79
HALF_T = 51.0                              # intermediate compartment  [min]
K      = np.log(2.0) / HALF_T
A_COEF = 2.0 * HALF_T ** (-1.0 / 3.0)      # ZH-L16-style M-value coefficients
B_COEF = 1.005 - HALF_T ** (-0.5)

PBOVP  = 0.13                              # gas-phase overpressure     [bar]
PMET   = 0.05                              # lumped metabolic gas       [bar]

DEPTH  = 18.0                              # the fixed stop depth        [m]
P_TIS0 = 3.56                              # starting supersaturated tension [bar]
DUR    = 130.0                             # minutes to show

p_amb   = P0 + DEPTH / 10.0                            # 2.80 bar
p_insp  = (p_amb - P_H2O) * FN2                        # inspired N2
p_cross = p_amb + PBOVP - PMET                         # inert tension at crossover
m_surf  = P0 / B_COEF + A_COEF                         # surfacing M-value

# linear slope = exponential slope evaluated at the crossover (continuity)
slope   = -K * (p_cross - p_insp)
t_cross = (P_TIS0 - p_cross) / (-slope)                # time to reach crossover

t = np.linspace(0, DUR, 1200)

# pure exponential desaturation
exp_curve = p_insp + (P_TIS0 - p_insp) * np.exp(-K * t)

# Thalmann: linear until t_cross, exponential afterwards
thal = np.where(
    t <= t_cross,
    P_TIS0 + slope * t,
    p_insp + (p_cross - p_insp) * np.exp(-K * np.clip(t - t_cross, 0, None)))

# --------------------------------------------------------------------------- #
fig, ax = plt.subplots(figsize=(10.5, 6.4))
C_EXP, C_THAL = "#1f6feb", "#d1242f"

ax.plot(t, exp_curve, color=C_EXP, lw=2.6, label="pure exponential (Bühlmann-like)")
ax.plot(t, thal, color=C_THAL, lw=2.6,
        label="Thalmann: linear, then exponential")

# crossover (linear -> exponential)
ax.scatter([t_cross], [p_cross], color=C_THAL, zorder=6, s=60,
           edgecolor="white", lw=1.2)
ax.annotate("crossover: linear → exponential\n"
            "(total tissue gas = P$_{amb}$ + PBOVP)",
            xy=(t_cross, p_cross), xytext=(t_cross + 6, p_cross + 0.42),
            fontsize=9.5, color=C_THAL,
            arrowprops=dict(arrowstyle="->", color=C_THAL))

# reference lines
ax.axhline(p_cross, color="#8250df", ls="-.", lw=1.2)
ax.text(DUR * 0.992, p_cross + 0.015, "gas-phase crossover line",
        ha="right", va="bottom", fontsize=8.5, color="#8250df")
ax.axhline(p_amb, color="#8250df", ls=":", lw=0.9, alpha=0.55)
ax.text(DUR * 0.992, p_amb - 0.05, "ambient pressure",
        ha="right", va="top", fontsize=8.5, color="#8250df", alpha=0.8)
ax.axhline(p_insp, color="#6e7781", ls="--", lw=1.2)
ax.text(DUR * 0.992, p_insp + 0.015, "inspired pN$_2$ (asymptote)",
        ha="right", va="bottom", fontsize=8.5, color="#6e7781")
ax.axhline(m_surf, color="#2da44e", ls=":", lw=1.6)
ax.text(DUR * 0.992, m_surf + 0.015, "M-value at surface",
        ha="right", va="bottom", fontsize=8.5, color="#2da44e")
ax.axhline(P0, color="#57606a", ls="-", lw=1.1)
ax.text(DUR * 0.992, P0 + 0.015, "surface pressure (1 bar)",
        ha="right", va="bottom", fontsize=8.5, color="#57606a")

# region shading: linear (slow) vs exponential washout for the Thalmann curve
ax.axvspan(0, t_cross, color=C_THAL, alpha=0.05)
ax.text(t_cross * 0.5, P_TIS0 - 0.07, "slow LINEAR washout",
        ha="center", fontsize=9.5, color=C_THAL)
ax.text((t_cross + DUR) / 2, P_TIS0 - 0.07, "EXPONENTIAL washout",
        ha="center", fontsize=9.5, color="#57606a")

# show the early gap (exponential off-gasses faster at first)
tg = 12.0
ax.annotate("", xy=(tg, np.interp(tg, t, exp_curve)),
            xytext=(tg, np.interp(tg, t, thal)),
            arrowprops=dict(arrowstyle="<->", color="#57606a"))
ax.text(tg + 2, (np.interp(tg, t, exp_curve) + np.interp(tg, t, thal)) / 2,
        "exponential is\nfaster early on", fontsize=8.5, color="#57606a")

ax.set_title(f"Desaturation of one compartment (t½ = {HALF_T:.0f} min) held at "
             f"{DEPTH:.0f} m\nThalmann washes out linearly first, then exponentially",
             fontsize=12.5)
ax.set_xlabel("Time at depth  [min]")
ax.set_ylabel("Tissue N$_2$ tension  [bar]")
ax.set_xlim(0, DUR)
ax.set_ylim(0.97, P_TIS0 + 0.12)
ax.legend(loc="upper right", framealpha=0.95)
ax.grid(alpha=0.25)
fig.tight_layout()
fig.savefig("/home/claude/fig_desat_crossover.png", dpi=150)

print(f"depth {DEPTH:.0f} m  | P_amb {p_amb:.3f} | P_insp {p_insp:.3f} | "
      f"crossover (inert) {p_cross:.3f} bar")
print(f"linear slope {slope:.5f} bar/min | reaches crossover at "
      f"t = {t_cross:.1f} min")
print("Figure written.")