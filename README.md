# The ten-degree rule is an undeclared Arrhenius model

The electrolytic-capacitor industry's standard life-derating shortcut — life doubles for every
10 °C the operating temperature drops below rated, halves for every 10 °C it rises — is usually
presented as a mechanism-free rule of thumb, independent of activation energy. **It is not.**
Solving the rule for the activation energy it implies shows the rule *is* an Arrhenius model,
with an `Ea` that changes depending on which temperature window and which extrapolation span you
apply it to. The rule never asks what the real damage mechanism is; this repository quantifies
what that silence costs.

> **Status: derivation proven, closed-form, reproducible with the standard library.** The
> deviation it predicts is confirmed independently by three manufacturers' own technical notes
> ([§4](#4-confirmed-independently-by-three-manufacturers)), and the implied `Ea` this repository
> derives is corroborated by a NASA reliability study ([§5](#5-what-the-published-ea-values-say)).

## TL;DR

- Solved the rule's own definition backwards for the Arrhenius activation energy `Ea` it implies.
- That `Ea` is **not constant — it varies 77%** depending on where on the temperature scale the
  rule is applied (0.549–0.971 eV across a sliding 10 °C window).
- Over the common 105 °C → 40 °C extrapolation the rule embeds **`Ea` = 0.707 eV**. A NASA
  reliability study independently states the rule "corresponds to an activation energy of
  ~0.68 eV" for liquid aluminum electrolytic capacitors — **within 4% of the derived value**.
  That 4% gap in `Ea` becomes a **19% gap in predicted hours**, which is the cheapest available
  proof that `Ea` is not a secondary detail.
- **The rule is right by coincidence, not by construction.** The only published `Ea` for the
  rule's exact target (liquid aluminum electrolytic) confirms it within 4%. But the rule carries
  no mechanism information, so nothing stops it being applied — as marketing shortcuts often are
  — to a neighbouring technology: across aluminum-polymer and tantalum-polymer capacitors, `Ea`
  measured in the same study ranges 0.57–1.03 eV, and carrying the rule there swings the error
  from **2.40× optimistic to 0.13× conservative**. See [§5](#5-checked-against-published-activation-energies--a-scope-correction)
  for exactly which value belongs to which technology — an earlier version of this repository
  blurred that distinction, and the correction is documented, not hidden.
- **Three competing manufacturers (Rubycon, Nichicon, Nippon Chemi-Con) independently confirm**
  the rule holds only in a bounded temperature window — see [`references.md`](references.md).
- Fully reproducible: standard-library-only `verify.py`, 14 automated tests, every citation
  traceable to a page number.

![Ea implied by the rule is not constant, and the resulting bias is directional](fig_ten_degree_rule.png)

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

The physical reason: Arrhenius is linear in `1/T`, not in `T`. The same 10 °C step spans a much
larger change in `1/T` down near 25 °C than it does up near 135 °C, so reproducing the same
`AF = 2` requires a smaller `Ea` at the cold end and a larger one at the hot end.

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

## 3. The cost of not asking: a sensitivity table

Fix a datasheet-typical scenario: 5,000 h rated at 105 °C, used at 40 °C. The rule predicts one
number — 452,548 h — **regardless of mechanism**. A true Arrhenius model predicts a different
number for each real `Ea`. The gap between them is the cost of the rule not asking:

| Ea real (eV) | rule predicts (h) | Arrhenius predicts (h) | rule / Arrhenius | verdict |
|---|---|---|---|---|
| 0.50 | 452,548 | 120,823 | **3.75×** | optimistic |
| 0.60 | 452,548 | 228,446 | **1.98×** | optimistic |
| 0.707 | 452,548 | 451,632 | 1.00× | **tautological, see below** |
| 0.80 | 452,548 | 816,687 | 0.55× | conservative |
| 0.90 | 452,548 | 1,544,157 | 0.29× | conservative |
| 1.00 | 452,548 | 2,919,626 | 0.16× | conservative |

> ⚠️ **The 1.00× row is not a validation of anything.** It compares the rule against an Arrhenius
> model carrying *the rule's own implied `Ea`*. Of course they agree: it is the same equation
> evaluated twice. Reading that row as "the rule is right" would be circular. The comparison that
> carries information is against activation energies established independently, which is [§5](#5-checked-against-published-activation-energies).

**This table is the deliverable, not any single row of it.** The error grows in both directions
away from the tautological point: roughly 4× optimistic at 0.50 eV, roughly 6× conservative at
1.00 eV. Which row applies to a given design depends on the real damage mechanism, which the rule
never asks about and the designer is rarely told.

**This repository deliberately does not claim which row is "the real one."** Doing so would
repeat the rule's own mistake — asserting an activation energy without establishing the
mechanism. What can be shown without that assumption is the shape and size of the sensitivity,
and that is what is above.

## 4. Confirmed independently by three manufacturers

**Rubycon Corporation** (doc. 3925-1e, §5-1) states the rule as `L = L0 * 2^((Tmax-Ta)/10)`,
presents it alongside a true Arrhenius curve (both anchored at 1.0 at 105 °C), and then states
directly:

> "The Arrhenius law and the '10°C 2 times law' show good consistency in the range of 70°C to
> 90°C, but there is some deviation of '10°C 2 times law' in the temperature range less than
> 60°C or more than 105°C."

**Nichicon Corporation** (CAT.8101H, §2-9-3) names the same rule "Arrhenius theory" and states
its applicability floor directly:

> "In general, if a capacitor is used at the maximum operating temperature or to a minimum of
> 40°C operating temperature the life expectancy can be calculated according to Arrhenius
> theory in which the life doubles for each 10°C drop in temperature."

**Nippon Chemi-Con** (technical FAQ, aluminum electrolytic capacitor lifetime) is the most
explicit of the three about the rule being an approximation with edges:

> "However, according to the Arrhenius Equation (6), the reciprocal of T is directly
> proportional to the logarithm of lifetime, which means that, strictly speaking, there is the
> temperature range where the theory of lifetime reducing by half at every 10°C rise is not
> applied."

They also bound where the doubling approximation actually holds: an acceleration factor of
"approximately 2" over **60 °C to 95 °C** — a 35-degree window, not the whole scale.

Three different manufacturers, three different documents, the same shape of caveat: the rule
holds in a bounded window, and each names where that window ends. **Nichicon's stated floor,
40 °C, is exactly the use temperature in §3's worked example** — the manufacturer's own
applicability limit sits at the edge of a routine extrapolation, not far past it. What this
repository adds is *how much* the deviation costs (§1–§3), which none of the three quantify.
Full citations and quotes-in-context in [`references.md`](references.md).

## 5. Checked against published activation energies — and a scope correction

§3's table sweeps round numbers. This section checks the derivation against activation energies
taken from a source read in full context: Teverovsky, A. (NASA GSFC / Jacobs Technology),
**"Stress Testing of Chip Aluminum Polymer Capacitors"**, PCNS proceedings.

**An earlier version of this section presented six values from that paper as if they were six
estimates of the same quantity — the uncertainty in `Ea` for the rule's own target component
(liquid aluminum electrolytic capacitors).** That was wrong, and it was the same failure mode as
the earlier unsourced claim in §Flagged, wearing a different disguise: this time the citation was
real, but its *scope* was not checked before the numbers went into a table together. Only one of
the six values is actually about the component this repository's rule targets. The other five are
about **neighbouring capacitor technologies** — corrected below.

| Ea (eV) | rule ÷ real | technology | source |
|---|---|---|---|
| 0.68 | **1.19×** | **liquid aluminum electrolytic** — the rule's own target | the rule's stated equivalence, per NASA |
| 0.57 | 2.40× | aluminum *polymer* (solid, no liquid electrolyte) | lower bound, measured ESR failures (that study) |
| 0.62 | 1.74× | tantalum *polymer* — a different base metal and electrolyte entirely | average cited in that study, ref. [17] |
| 0.73 | 0.87× | aluminum *polymer* | average measured in that study |
| 0.94 | 0.23× | aluminum *polymer* | CDE's published `Ea` in their own life equation |
| 1.03 | 0.13× | aluminum *polymer* | upper bound, measured ESR failures (that study) |

**Only the first row shares the rule's exact target component.** It gives a single, well-anchored
check: `Ea` = 0.68 eV against the 0.707 eV derived here, a 1.19× error — see the exact-match
discussion below. The other five rows measure aluminum-polymer and tantalum-polymer capacitors,
which do not carry liquid electrolyte and do not degrade by the mechanism (electrolyte
evaporation through the seal) this rule was written for. Reporting them next to the liquid-type
value as if they resolved the same uncertainty would be equivocation — the same word, "capacitor,"
covering two different populations in the same argument.

**What the five neighbouring values still show, correctly scoped:** even within one broad
engineering family — electrolytic-style capacitors built around aluminum or tantalum — the
activation energy is not a fixed property of "the capacitor." It swings from 0.57 to 1.03 eV
across technologies that a designer could plausibly confuse under the same rule of thumb. If
someone carries the 10-degree rule across that boundary — treating a polymer part's life like a
liquid electrolytic's, which is an easy mistake since both ship in the same case outlines and
both are marketed with the same doubling shortcut — the error swings from 2.40× optimistic to
0.13× conservative. **That is a real finding. It is a finding about transferring the rule across
component families, not about the uncertainty of one family's own mechanism.**

### The rule's stated equivalence, and what it costs

The NASA text states the equivalence directly:

> "The expected lifetime of liquid aluminum electrolytic capacitors is assumed to double when
> temperature is reduced by 10 °C, L ~ 2^(ΔT/10), **which corresponds to an activation energy of
> ~0.68 eV.**"

Read the scope carefully: this is NASA performing *the same conversion this repository performs*,
anchored at a different point on the curve. It is independent corroboration of the **method**
(someone else converted the rule to an `Ea` and landed nearby), not an independent measurement of
the underlying mechanism.

And the small gap between the two is itself the cheapest available demonstration of why `Ea`
matters:

```
derived  0.707 eV      published  0.68 eV
disagreement in Ea ................  4.0%
disagreement in predicted hours ... 19.0%
```

**Two sources that essentially agree still differ by a fifth of the answer**, because `Ea` sits in
an exponent. Anyone who treats the activation energy as a secondary detail is discarding 19% of
the result on a rounding difference.

**The honest conclusion, correctly scoped.** For liquid aluminum electrolytic capacitors over
this span, the rule's hidden `Ea` lands close to the one value actually published for that exact
component (~0.68 eV against 0.707 eV derived) — a 4% gap in `Ea`, 19% in predicted hours. The
rule works here. But it works without carrying any mechanism information, so it cannot signal
when it stops working: at a different span (§2), a different window (§1), or a different
*technology* whose dominant mechanism sits elsewhere in the 0.57–1.03 eV band measured for
neighbouring capacitor families (§5 above), the same rule produces the errors shown with exactly
the same confidence — and nothing about the rule's formula would tell you which case you are in.

> A rule that is right for reasons it cannot state is a rule you cannot audit. That is the
> finding — not that the number is wrong.

## Open

No manufacturer among those checked (Rubycon, Nichicon, Nippon Chemi-Con, Panasonic) publishes a
numeric `Ea` in eV in the documents examined; all four give the rule and its bounds in words and
figures, not in a parameter. The NASA source in §5 supplies the corroborating number instead.

A separate, still-unresolved question is the `Ea` of the *specific* dominant damage mechanism
(electrolyte evaporation through the seal) as distinct from the aggregate lifetime behaviour
quoted above. See [`references.md`](references.md) for what was searched and what was found —
including one candidate source that could not be read directly and is flagged rather than cited.

## Method note

All numbers here follow directly from the Arrhenius equation and the rule's own definition —
there is no fitting, no measured dataset, and no proprietary source. `verify.py` recomputes
every table in this README from first principles; running it also writes the three tables to
`data/` as CSV. `tests/` covers every headline number with pytest — `python3 -m pytest tests/ -v`.

The figure above is generated by `plot.py`, kept separate on purpose: `verify.py` stays
standard-library-only, and only `plot.py` needs matplotlib. Regenerate it with
`pip install matplotlib && python3 plot.py`.

Related public work: [`weibayes-zero-failures`](https://github.com/marcospaula/weibayes-zero-failures)
(same audit method, applied to a different shortcut — and the same discipline of reporting a
sensitivity instead of asserting the one true parameter) and
[`relengy`](https://github.com/marcospaula/relengy) (the reliability library this analysis reuses
the Arrhenius/AF conventions from — see `src/relengy/quantitative/alt.py`).
