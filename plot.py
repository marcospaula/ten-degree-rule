"""Generate the README figure. Optional -- verify.py stays dependency-free;
only this script needs matplotlib.

Run:  pip install matplotlib && python3 plot.py
"""

from __future__ import annotations

import matplotlib.pyplot as plt

from verify import arrhenius_life, implied_ea, ten_degree_rule_af

FIG_PATH = "fig_ten_degree_rule.png"


def main() -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))

    # --- Panel 1: Ea implied by the rule, sliding 10 C window ---
    hots = list(range(135, 34, -5))  # matches the README table exactly: 135->125 .. 35->25
    eas = [implied_ea(t, t - 10, af=2.0) for t in hots]
    ax1.plot(hots, eas, marker="o", color="#c0392b")
    ax1.axhspan(min(eas), max(eas), color="#c0392b", alpha=0.08)
    ax1.set_xlabel("hot end of the 10 C window (°C)")
    ax1.set_ylabel("Ea implied (eV)")
    ax1.set_title("The rule's implied Ea is not constant")
    ax1.invert_xaxis()
    ax1.annotate(f"{min(eas):.2f}–{max(eas):.2f} eV\n(77% spread)",
                 xy=(0.5, 0.08), xycoords="axes fraction", ha="center",
                 fontsize=9, color="#c0392b")

    # --- Panel 2: bias of the rule vs a true Arrhenius model, 105->40 C ---
    l_rated, t_rated, t_use = 5000.0, 105.0, 40.0
    l_rule = l_rated * ten_degree_rule_af(t_rated, t_use)
    eas2 = [0.45 + 0.01 * i for i in range(56)]  # 0.45 .. 1.00
    ratios = [l_rule / arrhenius_life(l_rated, t_rated, t_use, ea) for ea in eas2]

    ax2.plot(eas2, ratios, color="#2c3e50")
    ax2.axhline(1.0, color="gray", linewidth=0.8, linestyle=":")
    ax2.axvline(0.707, color="gray", linewidth=0.8, linestyle=":")
    ax2.fill_between(eas2, ratios, 1.0, where=[r > 1.0 for r in ratios],
                      color="#c0392b", alpha=0.15, label="rule optimistic")
    ax2.fill_between(eas2, ratios, 1.0, where=[r <= 1.0 for r in ratios],
                      color="#2980b9", alpha=0.12, label="rule conservative")
    ax2.scatter([0.707], [1.0], color="#c0392b", zorder=5)
    ax2.annotate("rule matches\nonly here (0.707 eV)", xy=(0.707, 1.0),
                 xytext=(0.78, 2.3), fontsize=9, color="#c0392b",
                 arrowprops=dict(arrowstyle="->", color="#c0392b"))
    ax2.set_xlabel("real activation energy Ea (eV)")
    ax2.set_ylabel("rule ÷ Arrhenius life prediction")
    ax2.set_title("105 °C → 40 °C: bias vs. the real mechanism")
    ax2.legend(fontsize=8, loc="upper right")

    fig.suptitle("The ten-degree rule embeds an undeclared, moving Arrhenius Ea",
                  fontsize=12, y=1.03)
    fig.tight_layout()
    fig.savefig(FIG_PATH, dpi=150, bbox_inches="tight")
    print(f"Wrote {FIG_PATH}")


if __name__ == "__main__":
    main()
