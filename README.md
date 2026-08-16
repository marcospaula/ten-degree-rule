# The ten-degree rule is an undeclared Arrhenius model

The electrolytic-capacitor industry's standard life-derating shortcut — life doubles for every
10 °C the operating temperature drops below rated, halves for every 10 °C it rises — is usually
presented as a mechanism-free rule of thumb, independent of activation energy. **It is not.**
Solving the rule for the activation energy it implies shows the rule *is* an Arrhenius model,
with an `Ea` that changes depending on which temperature window and which extrapolation span you
apply it to — and the direction of the resulting error is predictable and, at typical
electrolytic-capacitor activation energies, dangerous rather than conservative.

> **Status: derivation proven, closed-form, reproducible with the standard library.**
> The natural next step — pulling published `Ea` values from long-life capacitor datasheets
> (Nichicon, Rubycon, Panasonic) to see how they compare to the 0.707 eV the rule embeds between
> 105 °C and 40 °C — is not done yet. See [Open](#open) below.

## ▶ Reproduce it

```bash
python3 verify.py     # standard library only, no dependencies
```

Every number below comes straight from the rule's own definition and Arrhenius' equation — there
is no proprietary or measured data in this repository; everything is derivable from public,
textbook physics.

## The rule

```
L(T_use) = L_rated * 2 ** ((T_rated - T_use) / 10)
```

Manufacturers publish rated life at a rated ambient temperature (commonly 105 °C, sometimes
85 °C), and the 10-degree rule extrapolates it down to the actual operating temperature.

## 1. The rule embeds an activation energy

Any Arrhenius acceleration factor between two temperatures can be written

```
AF = exp[ Ea/k * (1/T_cold - 1/T_hot) ]
```

Setting `AF = 2` (the rule's own definition for a 10 °C step) and solving for `Ea` gives the
activation energy the rule assumes **in that window**:

| window (°C) | Ea implied (eV) |
|---|---|
| 135 → 125 | 0.971 |
| 105 → 95 | 0.832 |
| 85 → 75 | 0.745 |
| 65 → 55 | 0.663 |
| 45 → 35 | 0.586 |
| 35 → 25 | 0.549 |

**Range: 0.549–0.971 eV — a 77% spread**, purely from where on the temperature scale the 10 °C
step is taken. A rule advertised as mechanism-free is quietly assuming a different failure
mechanism at every point on the curve.

## 2. The Ea it embeds also depends on how far you extrapolate

Manufacturers apply the rule over one big jump — rated temperature to actual use temperature —
not a single 10 °C step. That changes the implied `Ea` again:

| from 105 °C to | Ea implied (eV) |
|---|---|
| 85 °C | 0.809 |
| 65 °C | 0.764 |
| 55 °C | 0.741 |
| 45 °C | 0.719 |
| **40 °C** | **0.707** |
| 25 °C | 0.673 |

The wider the extrapolation, the lower the implied `Ea` — the rule gets *less* conservative,
not more, the further you push it past its calibration point.

## 3. The direction of the error, at a realistic use temperature

Fix a datasheet-typical scenario: 5,000 h rated at 105 °C, used at 40 °C. Compare what the rule
predicts against what a true Arrhenius model predicts, at several `Ea` values plausible for
electrolyte evaporation and related wear-out mechanisms:

| Ea real (eV) | rule predicts (h) | Arrhenius predicts (h) | rule / Arrhenius | verdict |
|---|---|---|---|---|
| 0.50 | 452,548 | 120,823 | **3.75×** | optimistic — dangerous |
| 0.60 | 452,548 | 228,446 | **1.98×** | optimistic |
| 0.707 | 452,548 | 451,632 | 1.00× | coincides (by construction) |
| 0.80 | 452,548 | 816,687 | 0.55× | conservative |
| 0.90 | 452,548 | 1,544,157 | 0.29× | conservative |
| 1.00 | 452,548 | 2,919,626 | 0.16× | conservative |

**The rule only matches reality at exactly the `Ea` it happens to embed for that span (0.707 eV
here). Below that, it overstates life — in the worst case shown, by nearly 4×.** Electrolyte
evaporation and related low-barrier wear-out mechanisms are commonly cited in the 0.4–0.7 eV
range, which puts a real design on the optimistic side of this table more often than the rule's
universal-shortcut reputation suggests.

## Why this matters

This is exactly Pitfall 2 of accelerated-life-test practice: *asking for "the activation energy"
already assumes a damage mechanism, and the acceleration factor is strongly sensitive to it.*
The ten-degree rule does not avoid that assumption — it makes it silently, and the assumption
changes depending on where and how far you apply the rule. A design margin computed with the
rule is a margin computed against an unstated, moving `Ea`.

## Open

Not yet done, and the natural next step: pull published `Ea` values from long-life electrolytic
capacitor datasheets (Nichicon, Rubycon, Panasonic all publish activation-energy constants for
their premium series) and compare them against the 0.707 eV the rule embeds at the common
105 °C → 40 °C span. If any published `Ea` falls below ~0.7 eV, the manufacturer's own datasheet
would be quietly contradicting the shortcut it recommends alongside it.

## Method note

All numbers here follow directly from the Arrhenius equation and the rule's own definition —
there is no fitting, no measured dataset, and no proprietary source. `verify.py` recomputes
every table in this README from first principles; running it also writes the three tables to
`data/` as CSV.

Related public work: [`weibayes-zero-failures`](https://github.com/marcospaula/weibayes-zero-failures)
(same audit method, applied to a different shortcut) and
[`relengy`](https://github.com/marcospaula/relengy) (the reliability library this analysis reuses
the Arrhenius/AF conventions from — see `src/relengy/quantitative/alt.py`).
