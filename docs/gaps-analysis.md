# Longevity gaps analysis — three time windows

_Generated 2026-07-17 by an autonomous research run (`auto/longevity-gaps`). Sources: three
independent research subagents, one per window, each cited in its own file:_
- **Engagement (last ~30 days):** [`research/window-30days.md`](../research/window-30days.md) — ran the `last30days` skill (Reddit/HN/GitHub live; X unauthenticated) + web.
- **Survival (last ~30 years):** [`research/window-30years.md`](../research/window-30years.md) — `last30years`, ranked by still-load-bearing evidence.
- **Civilizational (last ~300 years):** [`research/window-300years.md`](../research/window-300years.md) — `last300years`, ranked by multi-generational survival.

> Discipline: **no evidence ⇒ no claim.** Every gap below is traced to ≥1 cited window. Gaps are
> ranked by **cross-window recurrence** — a gap that shows up in the 30-day chatter *and* the
> 30-year survivors *and* the 300-year record is far more real than a one-window fashion.

---

## The one-line finding

Across 30 days, 30 years, and 300 years, the field's deepest recurring gap is not a missing
therapy — it's **the inability to measure aging in a shared, validated, reproducible way.** You
cannot optimize what you cannot measure, and three independent time-horizons all land there.

---

## Gaps ranked by cross-window recurrence

### 🔴 Tier 1 — present in ALL THREE windows (highest confidence)

**G1. We cannot measure aging in a shared, validated way.**
- _30d:_ "epigenetic clocks contradict each other; no consensus clock has won" — users want one trustworthy individual read-out.
- _30y:_ "no shared cross-study benchmark / held-out leaderboard; clocks trained & tested on the same repos → publication bias; causal clocks still don't beat correlational ones."
- _300y:_ "200 years after Gompertz gave mortality a law, no aging biomarker is a validated regulatory surrogate endpoint — trials must still wait for death/disease."
- **Why it's the crux:** every downstream ambition (trials, comparison, capital allocation) is gated on it. It is also **the most computational and the most repo-shaped** of all the gaps.

**G2. Data integrity & reproducibility are unsolved.**
- _30d:_ Newman's supercentenarian/Blue-Zones "data is corrupted" critique is a live credibility reckoning; "where is the freakin list?" — big screens ship figures, not queryable data.
- _30y:_ "no reproducibility/replication infra beyond mice; no FAIR data + metadata standards for multi-omic aging data" (fragmentation blocks foundation-model training).
- _300y:_ the enduring principle "measure mortality before intervening; the fair test" — the discipline the field keeps violating.

**G3. Translation & hard endpoints — biomarkers ≠ outcomes.**
- _30d:_ the rapamycin backlash — "human efficacy on hard endpoints, not just biomarkers."
- _30y:_ "no standardized preclinical→human translation gate; no regulator-qualified surrogate endpoints; nearly every graveyard bet died in the mouse→human jump."
- _300y:_ "the translation gap — the oldest lever (CR, 1935) doesn't translate cleanly; aging isn't a disease, so there's no surrogate endpoint."

### 🟠 Tier 2 — two windows

**G4. Hype outruns evidence; nulls go unrecorded.** Graveyards recur every window — _300y_ (monkey glands, miasma, autointoxication), _30y_ (resveratrol/Sirtris ~$720M, NAD boosters, young blood), _30d_ (rapamycin over-claim, Blue-Zones fraud). The field has **no shared registry of honest nulls**; each generation re-learns the same failures.

**G5. Which theory? (programmed/epigenetic vs. stochastic damage).** _30d_ (active programmed-vs-damage fight) + _300y_ (evolutionary theory says no master switch, antagonistic-pleiotropy trade-offs). Capital is being allocated without a decisive answer.

**G6. Complexity / no master switch → the AI-native opening.** _300y_ names it explicitly: "single-target biotech ignores antagonistic pleiotropy — **the regime where AI-native whole-system modeling could add real value**"; _30y_ echoes it as the immaturity of aging-specific benchmarks for biology foundation models.

### 🟡 Tier 3 — one window, still notable
- **G7. Capital concentration** (_30d_): H1-2026 longevity funding was extreme-top-heavy (top-3 deals ≈ 75%; reprogramming ≈ 46%), starving non-reprogramming mechanisms.
- **G8. Healthspan–lifespan gap widening** (_300y_): ~8.5 yr (2000) → ~9.6 yr (2020); we extended dying, not living.
- **G9. Aging not classified as a disease** (_300y_): routes capital/regulation around the root cause.
- **G10. Erosion of past wins / AMR stewardship** (_300y_): a civilizational win is a maintained system, not a trophy.

---

## What THIS repo can actually bridge

Most Tier-1/2 gaps are wet-lab, regulatory, or capital problems — **no agent closes those in a
day, and claiming otherwise would violate the repo's own rule.** But the gaps are ranked to point
at the one this repo is *built* to attack:

**G1 (measurement) + G2 (reproducibility) are computational, open-data, and code-only — and they
are already the repo's North Star** (the Biolearn / Biomarkers-of-Aging leaderboard). The triangulation
says: the single highest-leverage artifact this loop can ship is **a standardized, reproducible,
open metric for _clock disagreement_** — turning "the clocks contradict each other" from a complaint
into a number anyone can compute the same way on the same data. That is the measurable core of G1,
it enforces G2's fair-test discipline, and it upgrades the already-scaffolded Turn 01 from a
one-off question into reusable infrastructure.

**Chosen bridge (this run):** `scripts/clockbench.py` — a deterministic, tested cross-clock
**disagreement benchmark** (pairwise agreement, rank-correlation, per-sample dispersion, consensus-vs-
outlier flags), runnable end-to-end today on a synthetic matrix, with a clean seam to plug in real
`pyaging`/Biolearn clock outputs — same honest-scaffold pattern as `baseline.py`. See the ROI ledger
for the before→after.

**Deliberately NOT bridged (queued / out of scope):** wet-lab validation (G3), a decisive aging
theory (G5), funding structure (G7), disease classification (G9) — flagged here so the omission is
honest, not silent.
