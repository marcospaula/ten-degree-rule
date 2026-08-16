# References

No PDF binaries are stored in this repository — sources are cited by URL, with the
specific passages that matter quoted and dated here. (Binary files are kept out of this
and every other repo in this workspace; only the distilled citation goes in.)

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

## Checked, no additional Ea data found

**Panasonic Industry Co., Ltd. "Hybrid/Aluminum Electrolytic Capacitor — Estimated
Lifetime Calculation Tool User Manual." ver 1.0, 2024-12-17.**
<https://industrial.panasonic.com/content/data/CC/PDF/Hybrid_Aluminum_Caparitor_Lifetime_Calculation_Manual_e.pdf>
(retrieved 2026-08-16)

A user manual for Panasonic's online lifetime calculator (screenshots, click-paths).
No activation energy, no life-vs-temperature formula, no Arrhenius discussion.
Checked so the search is not repeated: **this document does not help.**

## Still open

Nichicon publishes long-life series datasheets but the manufacturer's own
domain (`nichicon.co.jp`, `nichicon.com`) is outside this workspace's network
egress allowlist, and no cached/alternate copy was located via search. If a
Nichicon `Ea` value turns up, the natural check is the same as Rubycon's: does it
sit inside or outside the 0.55–0.97 eV band this repository's sliding-window
calculation produces.
