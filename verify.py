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
            "conservative" if ratio < 0.95 else "tautological")
        rows.append({
            "ea_real_ev": ea, "life_rule_h": round(l_rule),
            "life_arrhenius_h": round(l_arr), "rule_over_arrhenius": round(ratio, 2),
            "verdict": verdict,
        })
    return rows


# --------------------------------------------------- the published Ea values
# Every value below was read in full context from Teverovsky, A., "Stress
# Testing of Chip Aluminum Polymer Capacitors" (NASA GSFC / Jacobs, PCNS).
# Nothing here comes from a search-engine summary. See references.md SS4-5.
#
# TECHNOLOGY MATTERS. Only ONE of these six values (0.68 eV) is measured on
# the rule's actual target component -- liquid aluminum electrolytic
# capacitors. The other five are aluminum-POLYMER or tantalum-POLYMER parts:
# solid conductive cathode, no liquid electrolyte, a different dominant aging
# mechanism. An earlier version of this file listed all six as if they were
# six estimates of the same quantity -- that was equivocation, caught after
# the user asked "why are we mixing populations?". Corrected here: each row
# now carries its technology explicitly, and no function may report a value
# without it.
PUBLISHED_EA = [
    (0.68, "liquid aluminum electrolytic", "the rule's own target: NASA's stated equivalence"),
    (0.57, "aluminum polymer", "lower bound, measured ESR failures (this study)"),
    (0.62, "tantalum polymer", "average cited in this study [ref 17]"),
    (0.73, "aluminum polymer", "average MEASURED in this study"),
    (0.94, "aluminum polymer", "CDE published Ea in their own APC life equation"),
    (1.03, "aluminum polymer", "upper bound, measured ESR failures (this study)"),
]


def check_published_ea(t_rated_c: float = 105.0, t_use_c: float = 40.0) -> list[dict]:
    """How wrong is the rule against each *published* Ea, at one fixed span?

    This is the honest version of `check_bias`: instead of sweeping arbitrary
    round numbers, it uses only activation energies that appear in a source
    that was read in full -- tagged with the actual component technology,
    because the technology, not just the number, decides whether a row is
    evidence about the rule's own target or about a neighbouring one.
    """
    l_rule = ten_degree_rule_af(t_rated_c, t_use_c)
    rows = []
    for ea, technology, source in PUBLISHED_EA:
        af_arr = math.exp((ea / K_BOLTZMANN_EV)
                          * (1.0 / celsius_to_kelvin(t_use_c)
                             - 1.0 / celsius_to_kelvin(t_rated_c)))
        ratio = l_rule / af_arr
        rows.append({
            "ea_ev": ea,
            "technology": technology,
            "is_rule_target": technology == "liquid aluminum electrolytic",
            "rule_over_real": round(ratio, 2),
            "direction": "optimistic" if ratio > 1 else "conservative",
            "source": source,
        })
    return rows


def check_ea_sensitivity(t_rated_c: float = 105.0, t_use_c: float = 40.0) -> dict:
    """The cheapest demonstration that Ea is not a detail.

    The rule's implied Ea at this span is 0.707 eV; NASA quotes ~0.68 eV for the
    same rule and the same component class. That is a 4% disagreement in Ea --
    and it becomes a ~19% disagreement in predicted hours, because Ea sits in an
    exponent. Two sources that essentially agree still differ by a fifth.
    """
    derived = ten_degree_rule_implied_ea(t_rated_c, t_use_c)
    published = 0.68
    af_rule = ten_degree_rule_af(t_rated_c, t_use_c)

    def af(ea):
        return math.exp((ea / K_BOLTZMANN_EV)
                        * (1.0 / celsius_to_kelvin(t_use_c)
                           - 1.0 / celsius_to_kelvin(t_rated_c)))

    return {
        "ea_derived_ev": round(derived, 4),
        "ea_published_ev": published,
        "disagreement_in_ea_pct": round(100 * (derived / published - 1), 1),
        "disagreement_in_hours_pct": round(100 * ((af_rule / af(published))
                                                  / (af_rule / af(derived)) - 1), 1),
    }


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
    print("\n  NOTE: the 1.00x row is TAUTOLOGICAL, not a validation -- it compares the")
    print("  rule against Arrhenius carrying the rule's own implied Ea. The useful")
    print("  comparison is against independently published values, below.")

    pub = check_published_ea()
    _print_table("The rule vs. PUBLISHED Ea values (105 C -> 40 C) -- all read in full context", pub)
    target = [r for r in pub if r["is_rule_target"]]
    neighbours = [r for r in pub if not r["is_rule_target"]]
    print(f"\n  ONLY {len(target)} row matches the rule's own target component "
          f"(liquid aluminum electrolytic): {target[0]['rule_over_real']:.2f}x")
    nn = [r["rule_over_real"] for r in neighbours]
    print(f"  The other {len(neighbours)} rows are NEIGHBOURING technologies (aluminum/tantalum")
    print(f"  polymer) -- carrying the rule across that boundary swings the error from "
          f"{min(nn):.2f}x to {max(nn):.2f}x.")
    print("  Do not read this as six estimates of one uncertainty. It is one confirmed")
    print("  point plus a caution about applying the rule outside its own technology.")

    sens = check_ea_sensitivity()
    print("\n=== Why Ea is not a detail ===")
    print(f"  derived (this repo) ....... {sens['ea_derived_ev']} eV")
    print(f"  published (NASA) .......... {sens['ea_published_ev']} eV")
    print(f"  they disagree by .......... {sens['disagreement_in_ea_pct']}% in Ea")
    print(f"  which becomes ............. {sens['disagreement_in_hours_pct']}% in predicted hours")
    print("  Two sources that essentially AGREE still differ by a fifth of the answer.")

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
    with open(DATA / "published_ea.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=pub[0].keys())
        w.writeheader()
        w.writerows(pub)
    print("\nWrote data/windows.csv, data/spans.csv, data/bias.csv, data/published_ea.csv")


if __name__ == "__main__":
    main()
