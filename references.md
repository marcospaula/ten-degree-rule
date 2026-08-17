# References

No PDF binaries are committed to this repository's git history — sources are cited by
URL below, with the specific passages that matter quoted and dated. Local copies of the
PDFs referenced here are kept in `materials/` for convenience during writing, but
that directory is git-ignored and never enters a commit; the citation and the quoted
passage are the durable record, not the binary.

**Evidence standard used here.** Sources are grouped by how they were actually verified:
read page-by-page (§1–§4), or found but not directly readable (§Flagged). That
distinction is kept explicit rather than flattened into a uniform-looking bibliography.

---

## 1. Rubycon Corporation — the rule, and its stated deviation

**"Aluminum Electrolytic Capacitor — Technical Notes."** Document 3925-1e.
<https://www.rubycon.co.jp/wp-content/uploads/products-aluminum/al-technical-note_en.pdf>
(retrieved 2026-08-16, read in full)

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
quantifies**: the rule drifts from a true Arrhenius model outside a bounded
calibration window. Rubycon states *that* it deviates and *roughly where*; this
repository's `verify.py` derives *how much*, in activation energy (77% spread across
the sliding window) and in predicted hours (the sensitivity table in README §3).

Also relevant, same section: Rubycon states life calculation "is mainly applied to
products with an upper category temperature limit of 105 °C or less" — the rule is
explicitly not claimed to generalize freely, which supports treating any single
global `Ea` (including the 0.707 eV implied at the common 105→40 °C span) as a
local approximation rather than a mechanism constant.

No numeric activation energy in eV appears in this document — Rubycon's Fig. 21 shows
the Arrhenius curve graphically, without a stated `Ea`.

## 2. Nichicon Corporation — independent confirmation, and the 40 °C floor

**"General Descriptions of Aluminum Electrolytic Capacitors" / "Application Guidelines
for Aluminum Electrolytic Capacitors."** Technical Notes, CAT.8101H.
<https://www.nichicon.co.jp/english/products/pdf/aluminum.pdf>
(retrieved 2026-08-16, read in full)

Section 2-9-3 "Ambient Temperature and Life", p. 22:

> "In general, if a capacitor is used at the maximum operating temperature or to a
> minimum of 40°C operating temperature the life expectancy can be calculated
> according to Arrhenius theory in which the life doubles for each 10°C drop in
> temperature (Fig 2-15)."

Two things matter here. First, Nichicon names the rule "Arrhenius theory" directly —
independent confirmation that this is not an ad hoc shortcut but a stated (if
unparameterized) physical model. Second: **Nichicon caps the rule's stated validity at
a minimum of 40 °C.** That is precisely the use temperature in this repository's worked
example (105 °C rated → 40 °C use, README §3) — the manufacturer's own applicability
floor sits exactly at the edge of a routine extrapolation, not far past it. Fig. 2-15
in the same section plots guaranteed-life lines (85 °C/2000 h, 105 °C/2000 h,
105 °C/3000 h, 105 °C/5000 h) only down to 45 °C ambient, one notch above that floor.

Like Rubycon, Nichicon publishes no numeric `Ea` in this document.

**Domain note:** `nichicon.co.jp` is outside this workspace's Bash network egress
allowlist (`curl` fails with exit 56), but `WebFetch` reached it directly and cached
the PDF, which was then read with native PDF parsing. No allowlist change was needed.

## 3. Nippon Chemi-Con — the most explicit statement that the rule is an approximation

**"Lifetime of Aluminum Electrolytic Capacitors" (technical FAQ).**
<https://www.chemi-con.co.jp/en/faq/detail.php?id=alLifetime>
(retrieved 2026-08-17, read in full)

Presents the Arrhenius equation with activation energy as a symbolic variable `E`, then
states the practical approximation and — unusually — its own limits:

> "the temperature acceleration factor (Bt) is approximately 2 over an ambient
> temperature range from 60°C to 95°C, which means that the lifetime is approximately
> halved for every 10°C rise in ambient temperature."

> "However, according to the Arrhenius Equation (6), the reciprocal of T is directly
> proportional to the logarithm of lifetime, which means that, strictly speaking, there
> is the temperature range where the theory of lifetime reducing by half at every 10°C
> rise is not applied."

This is the third independent manufacturer confirming the same thing, and the most
direct of the three: the doubling rule is a **local approximation to Arrhenius valid in
a 35-degree window (60–95 °C)**, and the reason it fails outside that window is exactly
the `1/T` non-linearity that README §1 quantifies. Chemi-Con names the mechanism of the
failure without putting a number on it.

No numeric `Ea` in eV is given — the equation uses `E` symbolically.

## 4. NASA / Teverovsky — the published Ea that corroborates the derivation

**Teverovsky, A. "Stress Testing of Chip Aluminum Polymer Capacitors."** Jacobs
Technology Inc., NASA/GSFC c.562, Greenbelt MD. Presented at PCNS (Passive Components
Networking Symposium).
<https://passive-components.eu/wp-content/uploads/2025/04/ORAL_Day-3_34_JACOBS-USA_Stress-test-of-Al-polymer-capacitors.pdf>
(retrieved 2026-08-17, read in full — 14 pp.)

Section I (Introduction), stating the conventional equivalence directly:

> "The expected lifetime of liquid aluminum electrolytic capacitors is assumed to double
> when temperature is reduced by 10 °C, L ~ 2^(ΔT/10), **which corresponds to an
> activation energy of ~0.68 eV.**"

**This is the independent check on this repository's central derivation.** README §2
derives `Ea` = 0.707 eV as the value the rule embeds over the 105 °C → 40 °C span; NASA
states ~0.68 eV for the same rule and the same component class — a 4% difference,
arrived at independently.

The same study's own accelerated-life measurements (high-temperature storage at 100,
125 and 150 °C on seven types of aluminum polymer capacitors, a neighbouring technology)
found, §III:

> "Activation energies of the degradation varied from 0.64 to 0.9 eV for capacitance and
> in somewhat wider range, from 0.57 to 1.03 eV for ESR failures. However, the average
> activation energies were practically the same, Ea_C = 0.73 ± 0.1 eV, and
> Ea_ESR = 0.73 ± 0.16 eV."

Both bracket the derived 0.707 eV. **Consequence for this repository's framing:** for
liquid aluminum electrolytic capacitors over this particular span, the rule's hidden
`Ea` lands close to the conventionally accepted one — the rule is right here, but by
coincidence rather than by construction, since it carries no mechanism information that
would tell a user when the coincidence stops holding.

⚠️ **Read the scope carefully.** The 0.68 eV quote is about the *rule's assumed
equivalence for liquid aluminum electrolytic capacitors*; the 0.73 eV measurements are
on *aluminum polymer* capacitors (a different construction, no liquid electrolyte). They
are consistent with each other and with the derivation, but they are not the same claim,
and this repository does not merge them.

## 5. Checked, no usable data

**Panasonic Industry Co., Ltd. "Hybrid/Aluminum Electrolytic Capacitor — Estimated
Lifetime Calculation Tool User Manual." ver 1.0, 2024-12-17.**
<https://industrial.panasonic.com/content/data/CC/PDF/Hybrid_Aluminum_Caparitor_Lifetime_Calculation_Manual_e.pdf>
(retrieved 2026-08-16)

A user manual for Panasonic's online lifetime calculator (screenshots, click-paths).
No activation energy, no life-vs-temperature formula, no Arrhenius discussion.
Recorded so the search is not repeated: **this document does not help.**

---

## Flagged: the "electrolyte evaporation ≈ 0.4 eV" claim — found, not verified

An earlier version of this repository's README asserted that "electrolyte evaporation and
related low-barrier wear-out mechanisms are commonly cited in the 0.4–0.7 eV range" with
**no citation at all**. That was an unsourced assertion, caught on audit — recorded here
rather than quietly deleted, per this project's own standard.

**Candidate source, never read directly:**

**Torki, J.; Joubert, C.; Sari, A. (2023). "Electrolytic capacitor: Properties and
operation." *Journal of Energy Storage*, 58, 106330.**
DOI: [10.1016/j.est.2022.106330](https://doi.org/10.1016/j.est.2022.106330)
(peer-reviewed review article, Université Claude Bernard Lyon 1 / Laboratoire Ampère)

A search-engine summary of this paper states: *"the activation energy for electrolyte
evaporation is of the order of 0.4 eV for aluminum electrolytic capacitors (AEC) and
1.2 eV for tantalum capacitors"*, and separately attributes ~0.94 eV to anodic alumina
degradation (a different aging mechanism in the same component).

**Why this stays flagged.** ScienceDirect, ResearchGate and the HAL open-archive mirror
all refused direct access (HTTP 403 / bot challenge, 2026-08-16 and 2026-08-17). The
0.4 eV figure comes from a search engine's summary, not from the primary text. That is a
weaker standard of evidence than sources §1–§4, all of which were read page-by-page.

**Why it no longer matters to the argument.** The README was restructured (2026-08-17) so
that no claim depends on knowing the true mechanism-specific `Ea`. §3 now presents the
full sensitivity across 0.50–1.00 eV and explicitly declines to name "the real one" —
which is the methodologically correct posture anyway, and happens to make this open
question non-blocking. If the Torki paper is ever read directly, it would add nuance
(mechanism-level `Ea` vs. the aggregate lifetime behaviour NASA quotes), not repair a
load-bearing gap.

**Note on the tension between the two numbers.** The flagged ~0.4 eV (mechanism-specific,
electrolyte evaporation) and the verified ~0.68 eV (aggregate rule equivalence for the
same component, §4) are not necessarily contradictory — they may describe different
levels of abstraction, since observed device lifetime aggregates several mechanisms, not
only evaporation. Resolving that would require the primary text. It is left open, not
guessed at.
