# References

No PDF binaries are committed to this repository's git history — sources are cited by
URL below, with the specific passages that matter quoted and dated. Local copies of the
three PDFs referenced here are kept in `materials/` for convenience during writing, but
that directory is git-ignored and never enters a commit; the citation and the quoted
passage are the durable record, not the binary.

## Primary source — confirms the deviation this repository quantifies

**Rubycon Corporation. "Aluminum Electrolytic Capacitor — Technical Notes."**
Document 3925-1e. Rubycon Corporation.
<https://www.rubycon.co.jp/wp-content/uploads/products-aluminum/al-technical-note_en.pdf>
(retrieved 2026-08-16)

Section 5-1 "Ambient Temperature and Life", p. 20, gives the rule as **Eq. 10**:

```
L = L0 * 2 ^ ((Tmax - Ta) / 10)
```

and states, immediately after presenting Fig. 21 (Arrhenius law vs. the 10 °C rule,
both anchored at 1.0 at 105 °C):

> "The Arrhenius law and the '10°C 2 times law' show good consistency in the range
> of 70°C to 90°C, but there is some deviation of '10°C 2 times law' in the
> temperature range less than 60°C or more than 105°C."

**This is the manufacturer's own admission of exactly the effect this repository
quantifies**: the rule is not mechanism-free, and it drifts from a true Arrhenius
model outside a narrow calibration window. Rubycon states *that* it deviates and
*roughly where*; this repository's `verify.py` derives *how much*, in activation
energy (77% spread across the sliding window) and in hours (up to ~4x optimistic at
a realistic 105 °C → 40 °C extrapolation, at activation energies plausible for
electrolyte evaporation).

Also relevant, same section: Rubycon states life calculation "is mainly applied to
products with an upper category temperature limit of 105 °C or less" — the rule is
explicitly not claimed to generalize freely, which supports treating any single
global `Ea` (including the 0.707 eV implied at the common 105→40 °C span) as a
local approximation rather than a mechanism constant.

No numeric activation energy in eV is published in this document — Rubycon's
Fig. 21 shows the Arrhenius curve graphically, without a stated `Ea`. That number,
and the quantified bias, are this repository's contribution.

## Second primary source — independent confirmation, same shape

**Nichicon Corporation. "General Descriptions of Aluminum Electrolytic Capacitors" /
"Application Guidelines for Aluminum Electrolytic Capacitors."** Technical Notes,
CAT.8101H. Nichicon Corporation.
<https://www.nichicon.co.jp/english/products/pdf/aluminum.pdf>
(retrieved 2026-08-16)

Section 2-9-3 "Ambient Temperature and Life", p. 22:

> "In general, if a capacitor is used at the maximum operating temperature or to a
> minimum of 40°C operating temperature the life expectancy can be calculated
> according to Arrhenius theory in which the life doubles for each 10°C drop in
> temperature (Fig 2-15)."

Two things matter here. First, Nichicon names the rule "Arrhenius theory" directly —
independent confirmation that this is not an ad hoc shortcut but a stated (if
unparameterized) physical model. Second, and more useful to this repository's
argument: **Nichicon caps the rule's stated validity at a minimum of 40 °C.** That
is precisely the use temperature in this repository's worked example (105 °C rated
→ 40 °C use, §3 of the README) — the manufacturer's own applicability floor sits
exactly at the edge of a routine extrapolation, not far past it. Fig. 2-15 in the
same section plots guaranteed-life lines (85 °C/2000 h, 105 °C/2000 h, 105 °C/3000 h,
105 °C/5000 h) only down to 45 °C ambient, one notch above that floor.

Like Rubycon, Nichicon publishes no numeric `Ea` in this document — only the rule
and its bounded range of applicability.

**Domain note:** `nichicon.co.jp` is outside this workspace's Bash network egress
allowlist (`curl` fails with exit 56), but `WebFetch` reached it directly and cached
the PDF, which was then read with native PDF parsing. No allowlist change was
needed for this source.

## Checked, no additional Ea data found

**Panasonic Industry Co., Ltd. "Hybrid/Aluminum Electrolytic Capacitor — Estimated
Lifetime Calculation Tool User Manual." ver 1.0, 2024-12-17.**
<https://industrial.panasonic.com/content/data/CC/PDF/Hybrid_Aluminum_Caparitor_Lifetime_Calculation_Manual_e.pdf>
(retrieved 2026-08-16)

A user manual for Panasonic's online lifetime calculator (screenshots, click-paths).
No activation energy, no life-vs-temperature formula, no Arrhenius discussion.
Checked so the search is not repeated: **this document does not help.**

## Still open

No manufacturer among the three checked (Rubycon, Nichicon, Panasonic) publishes a
numeric `Ea` in eV. Both Rubycon and Nichicon confirm the rule's limited range of
validity in words and figures, not in a parameter that could be compared directly
against the 0.707 eV this repository derives at the 105→40 °C span. A long-life
premium-series datasheet (rather than these general technical notes) is the next
place to look, if the exact number is still wanted.

## Flagged: the "0.4–0.7 eV for electrolyte evaporation" claim is not independently verified

An earlier version of this repository's README (§3) stated that "electrolyte evaporation
and related low-barrier wear-out mechanisms are commonly cited in the 0.4–0.7 eV range"
with no citation. That was an unsourced assertion, caught on audit — recorded here rather
than quietly corrected, per this project's own standard (see the git history for the fix).

**Candidate source, not yet confirmed by direct reading:**

**Torki, J.; Joubert, C.; Sari, A. (2023). "Electrolytic capacitor: Properties and
operation." *Journal of Energy Storage*, 58, 106330.**
DOI: [10.1016/j.est.2022.106330](https://doi.org/10.1016/j.est.2022.106330)
(peer-reviewed review article, Université Claude Bernard Lyon 1)

A search-engine summary of this paper states: *"the activation energy for electrolyte
evaporation is of the order of 0.4 eV for aluminum electrolytic capacitors (AEC) and
1.2 eV for tantalum capacitors"*, and separately attributes ~0.94 eV to anodic alumina
degradation (a different aging mechanism in the same component).

**Why this is flagged instead of cited normally:** both ScienceDirect and ResearchGate
returned HTTP 403 (paywalled) when fetched directly (2026-08-16). The 0.4 eV figure above
comes from a search engine's summary of the paper, not from reading the primary text.
That is not the same standard of evidence as the Rubycon and Nichicon citations above,
which were read page-by-page. Do not upgrade this to a cited fact until the full text is
read directly and the exact passage is quoted in context.
