"""Reproduce every result of the ten-degree-rule audit. Standard library only.

The "10 degree rule" is the industry-standard shortcut for electrolytic
capacitor life: life doubles for every 10 C the operating temperature drops
below the rated temperature (equivalently, halves for every 10 C rise).

    L(T_use) = L_rated * 2 ** ((T_rated - T_use) / 10)

It is usually presented as a mechanism-free rule of thumb. This script shows
it is not: solving the rule for an Arrhenius activation energy Ea shows the
rule IS an Arrhenius model, with an Ea that the rule itself fixes -- and that
Ea is not constant. It depends on which 10 C window, and which extrapolation
span, you apply the rule to.

Run:  python3 verify.py
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

DATA = Path(__file__).parent / "data"

K_BOLTZMANN_EV = 8.617333262e-5  # eV/K, CODATA 2018


def celsius_to_kelvin(c: float) -> float:
    return c + 273.15


def implied_ea(t_hot_c: float, t_cold_c: float, af: float) -> float:
    """Ea (eV) that makes an Arrhenius model reproduce a given AF between two
    temperatures (t_hot is the higher/stressed temperature).

    AF = exp[ Ea/k * (1/T_cold - 1/T_hot) ]  =>  Ea = k * ln(AF) / (1/T_cold - 1/T_hot)
    """
    if t_hot_c <= t_cold_c:
        raise ValueError("t_hot_c must be greater than t_cold_c")
    if af <= 1.0:
        raise ValueError("af must be > 1 for a hot-to-cold comparison")
    t_hot, t_cold = celsius_to_kelvin(t_hot_c), celsius_to_kelvin(t_cold_c)
    return K_BOLTZMANN_EV * math.log(af) / (1.0 / t_cold - 1.0 / t_hot)


def ten_degree_rule_af(t_rated_c: float, t_use_c: float) -> float:
    """AF of the 10-degree rule between the rated and the use temperature."""
    if t_use_c >= t_rated_c:
        raise ValueError("t_use_c must be below t_rated_c for the rule to accelerate")
    return 2.0 ** ((t_rated_c - t_use_c) / 10.0)


def ten_degree_rule_implied_ea(t_rated_c: float, t_use_c: float) -> float:
    """Ea (eV) that the 10-degree rule embeds, for a given rated/use pair."""
    af = ten_degree_rule_af(t_rated_c, t_use_c)
    return implied_ea(t_rated_c, t_use_c, af)


def arrhenius_life(l_rated: float, t_rated_c: float, t_use_c: float, ea_ev: float) -> float:
    """Life at t_use_c predicted by a true Arrhenius model with a given Ea."""
    t_rated, t_use = celsius_to_kelvin(t_rated_c), celsius_to_kelvin(t_use_c)
    af = math.exp((ea_ev / K_BOLTZMANN_EV) * (1.0 / t_use - 1.0 / t_rated))
    return l_rated * af


# --------------------------------------------------------------------- checks

def check_windows() -> list[dict]:
    """Ea implied by the rule across a sliding 10 C window -- shows it is NOT constant."""
    rows = []
    for t_hot in range(135, 25, -10):
        t_cold = t_hot - 10
        ea = implied_ea(t_hot, t_cold, af=2.0)
        rows.append({"window_c": f"{t_hot}->{t_cold}", "ea_ev": round(ea, 4)})
    return rows


def check_spans(t_rated_c: float = 105.0) -> list[dict]:
    """Ea implied by the rule as the extrapolation span from t_rated widens."""
    rows = []
    for t_use in (85, 65, 55, 45, 40, 25):
        ea = ten_degree_rule_implied_ea(t_rated_c, t_use)
        rows.append({"t_rated_c": t_rated_c, "t_use_c": t_use, "ea_implied_ev": round(ea, 4)})
    return rows


def check_bias(l_rated: float = 5000.0, t_rated_c: float = 105.0, t_use_c: float = 40.0) -> list[dict]:
    """For a fixed rated life/temperature, compare the rule's prediction against
    a true Arrhenius model at several plausible real activation energies."""
    l_rule = l_rated * ten_degree_rule_af(t_rated_c, t_use_c)
    rows = []
    for ea in (0.50, 0.60, 0.707, 0.80, 0.90, 1.00):
        l_arr = arrhenius_life(l_rated, t_rated_c, t_use_c, ea)
        ratio = l_rule / l_arr
        verdict = "OPTIMISTIC (dangerous)" if ratio > 1.05 else (
            "conservative" if ratio < 0.95 else "coincides")
        rows.append({
            "ea_real_ev": ea, "life_rule_h": round(l_rule),
            "life_arrhenius_h": round(l_arr), "rule_over_arrhenius": round(ratio, 2),
            "verdict": verdict,
        })
    return rows


def _print_table(title: str, rows: list[dict]) -> None:
    print(f"\n=== {title} ===")
    if not rows:
        return
    cols = list(rows[0].keys())
    widths = {c: max(len(c), *(len(str(r[c])) for r in rows)) for c in cols}
    print("  ".join(c.ljust(widths[c]) for c in cols))
    for r in rows:
        print("  ".join(str(r[c]).ljust(widths[c]) for c in cols))


def main() -> None:
    print("Ten-degree-rule audit -- reproducing every published number.")

    windows = check_windows()
    _print_table("Ea implied by the rule, sliding 10 C window", windows)
    ea_values = [r["ea_ev"] for r in windows]
    print(f"\nrange: {min(ea_values):.3f} - {max(ea_values):.3f} eV "
          f"({100*(max(ea_values)/min(ea_values)-1):.0f}% spread)")

    spans = check_spans()
    _print_table("Ea implied by the rule, extrapolating from 105 C", spans)

    bias = check_bias()
    _print_table("Bias of the rule vs. a true Arrhenius model (105 C -> 40 C, L_rated=5000 h)", bias)

    with open(DATA / "windows.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=windows[0].keys())
        w.writeheader()
        w.writerows(windows)
    with open(DATA / "spans.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=spans[0].keys())
        w.writeheader()
        w.writerows(spans)
    with open(DATA / "bias.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=bias[0].keys())
        w.writeheader()
        w.writerows(bias)
    print(f"\nWrote data/windows.csv, data/spans.csv, data/bias.csv")


if __name__ == "__main__":
    main()
