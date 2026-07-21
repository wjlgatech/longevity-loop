# OpenSpace trial — results (verified 2026-07-20)

Source-installed **HKUDS/OpenSpace** v2.0.0 (MIT) in a Python 3.12.13 venv, registered
longevity-loop's skills, ran 3 real tasks headless (`--no-ui --query`, model
`anthropic/claude-sonnet-4-5` via litellm), and read the quality records OpenSpace emits into
`.openspace/evidence.db` + `.openspace/openspace.db`. This is evidence, not vibes — the numbers below
are dumped straight from those DBs.

## Setup outcome
- **Install:** `pip install .` (non-editable). Editable install was broken — see RUNBOOK.md gotcha.
- **Registered skills** (→ `.openspace/skills/<name>/SKILL.md`, all imported `trust_state=trusted`):
  `longevity-loop`, `compute-aging-clocks`, `biolearn-leaderboard`.
- **Scope note (honest):** OpenSpace also auto-scanned `~/.claude/skills` and imported the whole
  global set (**69** `skill_records` total — 10xgoal, graphify, etc.), not just the 3 project skills.
  Worth knowing for scope/privacy; only the 3 project skills were exercised.

## The 3 tasks — quality records
| Task | Skill targeted | Status | Skill applied? (OpenSpace judgment) |
|---|---|---|---|
| 1 · pyaging clock-panel plan | compute-aging-clocks | ✅ SUCCESS (`completed=True`, 3 iters) | **not formally judged** (`skills_judged=0`) — note: *"provided a concrete plan with exact pyaging API calls"*, attributed to model knowledge |
| 2 · Biolearn challenge-data + submission | biolearn-leaderboard | ✅ SUCCESS (2 iters) | **YES** — *"the skill was loaded and its instructions were directly used to construct the plan"*; trust observation = success |
| 3 · loop target + low-hanging fruit | longevity-loop | ✅ SUCCESS (2 iters) | **YES** — *"invoked successfully; the agent extracted the loop's target"*; trust observation = success |

**Per-skill counters** (`skill_records`): biolearn-leaderboard applied 1 / completed 1 / fallbacks 0 ·
longevity-loop applied 1 / completed 1 / fallbacks 0 · compute-aging-clocks 0/0/0 (registered, not
formally applied in these runs).

**Tool reliability** (`tool_quality_records`): `Skill` 2/5 successful calls · `bash` 0/1 · `write`
0/2 · `ls` 1/1.

**Evolution engine:** all analyses → **NOOP** (no skill mutation admitted). Recorded reasons:
*"procedure refs lack execution"*, *"no evolution suggestion"* — the plan/summarize tasks produced no
executed evidence to justify evolving a skill. Honest outcome, not a failure.

## Two findings that matter
1. **OpenSpace's sandbox denied `bash`/`write` by default** (`permission_denied`). Good for blast
   radius — the agent could not execute code or write files — but it's *why* the pyaging task
   produced a plan rather than a computed clock panel. To run execution-heavy tasks, grant those
   tool permissions explicitly.
2. **Skills register cleanly into a third-party quality-first hub and are selected + applied on
   relevant tasks** — 2 of 3 with an explicit "skill applied" judgment, all 3 completed. Same
   SKILL.md format as the longevity-loop hub, so no adaptation was needed.

## Verdict (trial protocol §Success criteria)
- ✅ Quality records for 3 real tasks (evidence in the two DBs).
- ✅ Skills correctly selected/applied (biolearn + longevity-loop judged applied).
- ⚠️ No **validated evolution** — the engine correctly declined (plans give no executed evidence);
  the criterion needs an execution-permitted task to be met.
- ⚠️ Tokens/latency not benchmarked vs a no-OpenSpace baseline this run.
- **Verdict: trial-more.** OpenSpace is a viable external validator of the loop's skills; the single
  number that would decide *adopt* is a **validated, no-regression evolution on an
  execution-permitted task** — not yet demonstrated.

_Scratch dirs (external, not committed): OpenSpace at `~/Documents/Projects/OpenSpace`; run dir at
`~/Documents/Projects/openspace-run/.openspace/{evidence,openspace}.db` + `logs/recordings/`._
