# Autonomous run — ROI ledger & decision log

**Run:** `auto/longevity-gaps` · started 2026-07-17 09:54 CDT · report due 18:00 CDT
**Operator:** away for the day. Agent is in charge, applying cofounder discipline by hand
(the `anyagent cofounder` subcommand isn't in the installed CLI v0.1.0 — artifact ≠ label).

## Mandate
1. Research longevity across three time windows (`/last30days` engagement · `/last30years`
   survival · `/last300years` civilizational) → `docs/gaps-analysis.md`.
2. Bridge the gaps that are actionable in this repo, ROI-positive, and reversible.
3. Monitor ROI: token/time/compute spent vs. before→after impact, weighted to **end-user**
   and **business** value, via AI-native engineering (harness + loop engineering).

## Guardrails I'm operating under (my well-thought defaults, since you can't approve mid-run)
- **Reversibility routing (cofounder-by-hand):**
  - 🟢 reversible (research files, new scripts/data on a branch, gated by `make check`) → I execute.
  - 🟡 batch (a judgement call with a clear recommendation) → I do it and log the rationale.
  - 🔴 irreversible / outward-facing (**merge to `main`, publish to the live portfolio, any spend
    past the budget ceiling, wet-lab or medical claims**) → I STOP and queue for your Verdict.
- **Budget ceiling:** research = 3 bounded parallel subagents (medium effort); bridging = at most
  the top 2 gaps by ROI. Stop at diminishing returns rather than "filling the day."
- **No evidence ⇒ no claim.** Research is cited; bridges ship a passing gate; no fabricated results.
- **Precise token metering isn't instrumented in this harness** — costs below are honest estimates
  (subagent count × effort, wall-clock), not billing-exact. Flagged as such.

## ROI method (before → after)
For each bridge: `metric` · `before` · `after` · `end-user impact` · `business impact` · `cost`.
A bridge ships only if after > before on a real, checkable metric AND the impact justifies the cost.

## Cost ledger (running)
| Phase | What | Est. cost | Wall-clock |
|---|---|---|---|
| 0 · setup | branch + ledger + scaffolding | ~small (1 session, few calls) | ~5 min |
| 1 · research | 3 parallel research subagents (30d/30y/300y) | ~medium (3 agents × ~15-25 searches) | est. 10-25 min |
| 2 · synthesis | gaps-analysis.md from the 3 window reports | ~small | est. 10 min |
| 3 · bridge | top-N reversible gaps, gated | ~medium | est. 30-90 min |

## Decision log (append-only)
- **09:54** — `anyagent cofounder` absent → apply the discipline by hand (routing above). Reversible.
- **09:54** — one interactive session ≠ literal all-day autonomy; deliver bounded high-value work
  now + queue irreversible forks. Chose quality/ROI over duration. Reversible.
- **09:56** — delegate the 3 research windows to background subagents (lean main context, parallel)
  rather than running the heavy research skills inline. Harness-engineering choice. Reversible.
- **~10:00** — window-30years agent done: 60.7k subagent tokens, 19 tool-uses, 4.3 min wall-clock
  (a real ROI datapoint — extrapolates to ~180k tokens for the 3-agent research phase). Gaps it
  surfaced converge hard on **shared cross-study biomarker benchmarks + a held-out leaderboard +
  honest-nulls / reproducibility infra** — the same computational gap this repo's own reflections
  named, now triangulated from the survival window. Strong signal the top bridge is benchmark/registry-shaped.
- **~10:06** — window-300years agent done: 63.9k subagent tokens, 16 tool-uses, 5.7 min. Research
  phase so far = **124.6k tokens / 2 agents** (on track for ~185k for all 3 — a real ROI number,
  not an estimate). Convergence across both completed windows is unusually tight: **aging is
  unmeasurable at regulatory grade + no shared held-out benchmark + no causal-clock validation**.
  Two independent time-horizons landing on the same computational gap ⇒ high-confidence this is the
  right bridge, and it's exactly repo-shaped (benchmark/leaderboard, not wet-lab).
- **~10:10** — window-30days agent done: 89.1k tokens, 23 tool-uses, 8.3 min (it installed the
  real `last30days` skill via npx; 4/5 live sources, X unauth). Engagement window independently
  confirms the measurement gap ("clocks contradict each other; no consensus clock has won").
- **~10:20** — all 3 windows agree → chose the bridge: **G1 measurement**, via a reproducible
  clock-disagreement benchmark. Reversible (new script + gated), highest cross-window recurrence,
  repo-shaped (it IS the North Star). Shipped `scripts/clockbench.py`, gated in `make check`.

---

## Results & ROI (before → after)

**D1 — `docs/gaps-analysis.md`** (cross-window, cited)
- before: scattered reflections, no ranked gap map · after: 10 gaps ranked by cross-window
  recurrence, #1 identified with evidence from all 3 windows.
- end-user: Paul knows exactly which gap to attack and why. business: focuses the loop's scarce
  effort on the single highest-leverage, most-defensible, North-Star-aligned gap — anti-scatter.

**D2 — `scripts/clockbench.py`** (the bridge)
- metric: a shared, reproducible way to quantify clock-panel disagreement.
- before: "clocks disagree" was an un-quantified complaint (no shared metric).
- after: deterministic Spearman-agreement benchmark + outlier detection + per-sample dispersion;
  CI-self-verifying; demo headline **0.315**; real-data seam via `--input`. `make check` green (100/100).
- **end-user impact:** any researcher runs ONE command to quantify disagreement on their own data —
  a reusable open tool (the roadmap's "ship a tool a lab adopts" thesis), not another clock.
- **business impact:** a concrete, credible, code-only artifact to compete on the Biolearn
  leaderboard and to open researcher conversations (Connections track) — differentiated infra.
- **AI-native engineering:** harness eng = 3 parallel background research agents (lean main context,
  artifacts on disk) vs inline heavy skills; loop eng = the bridge self-verifies in CI, extends the
  eval-gated execution ledger (E17), and is byte-deterministic (fair-test discipline).

## Final cost (honest, not billing-exact)
| Item | Cost |
|---|---|
| Research (3 subagents) | **213.7k tokens** (60.7k + 63.9k + 89.1k), 58 tool-uses, ~8 min wall-clock (parallel) |
| Synthesis + bridge (main loop) | not metered; est. tens-of-k tokens, ~30 min wall-clock |
| **Total wall-clock** | **~45 min** (09:54 → ~10:40) — vs a full day; stopped at diminishing returns, not the clock |

## 🔴 Queued for your Verdict (I did NOT auto-execute)
1. **Merge `auto/longevity-gaps` → `main`?** Everything is on a branch + PR, CI-green. Merge is the
   one irreversible step; it's yours. (One-click on return.)
2. **Nothing published outward** this run (no site/portfolio change) — so merge is the only gate.
3. Out-of-scope-by-design (not attempted): wet-lab validation, a decisive aging theory, funding
   structure — flagged in gaps-analysis.md so the omissions are honest, not silent.
