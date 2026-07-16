# Turn 01 — Systems-Age-motivated baseline on the Biomarkers of Aging Challenge

*One turn of the [loop](../../README.md#the-loop). **Scaffold** — run it, then fill
[`PROOF.md`](PROOF.md). No result claimed until PROOF is filled (no evidence ⇒ no claim).*

**Anchored to a frontier work:** Morgan Levine's *Systems Age* (Nature Aging, 2025) —
*"most epigenetic clocks provide a single age estimate, overlooking within-person variation"*
([paper](https://www.nature.com/articles/s43587-025-00958-3)). We test a cheap, code-only proxy of
that thesis on the open leaderboard data, then send the result to her (@DrMorganLevine).

## ① QUESTION (falsifiable)
Does **cross-clock disagreement** — the heterogeneity across a panel of epigenetic clocks (a poor-man's
proxy for Levine's multi-system aging) — **add predictive signal over the single best clock** for the
challenge outcome?
- **Metric:** outcome AUROC of `[best-single-clock age-accel]` vs `[best-single + across-clock std]`, on a fixed held-out split, mean ± std over 5 seeds. Report Δ.
- **Null I accept:** CIs overlap ⇒ "heterogeneity adds nothing here" — a clean, reportable null that still engages Levine's thesis.

## ② DATA (open)
[Biomarkers of Aging Challenge](https://www.longevityprize.com/prize/biomarker) dataset via
**[Biolearn](https://bio-learn.github.io/)**. Public methylation + outcomes only; nothing wet-lab.

## ③ MODEL
Compute a **panel** of clocks (Horvath, PhenoAge, GrimAge, DunedinPACE…) with Biolearn / `pyaging`;
features = best-single-clock acceleration, and + the std/spread across the panel (the heterogeneity signal).

## ④ VERIFY
Held-out split, 5 seeds; submit to the public leaderboard if open. The leaderboard rank is the external verifier.

## ⑤ WRITE-UP → fill [`PROOF.md`](PROOF.md)
Result **and** the null; threats-to-validity; reproduce command.

## ⑥ SHARE
Commit the turn + an honest thread; **send it to Morgan Levine** — a code-only test of her Systems-Age
thesis on open data is a genuine, non-cringe reason to reach out (Connections track).

## ⑦ COMPOUND
If heterogeneity helps, Turn 02 upgrades the proxy toward true system-specific clocks (a real Systems-Age
reproduction) via a bio-FM. If it's a null, that's itself a finding worth sharing.

## Run it
```bash
cd turns/turn-01-biolearn-baseline
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python baseline.py            # prints the Δ (heterogeneity lift) across seeds; writes results.json
# then fill PROOF.md with the real numbers (including a null if that's what you got)
```
