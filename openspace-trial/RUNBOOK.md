# OpenSpace trial — longevity-loop

Evaluate whether **HKUDS/OpenSpace** improves this repo's tooling quality (observe → evolve) with no
regression/bloat/slowdown. Local-first; own-your-data.

## ⚠️ Install correctly (verified 2026-07-20)
**Do NOT `pip install openspace`** — that PyPI name is a *different, unrelated* package
("astrodynamics analysis and simulation", Brandon Sexton, GPLv3). Name ≠ identity. HKUDS installs from source:
```
git clone https://github.com/HKUDS/OpenSpace.git && cd OpenSpace
python3.12 -m venv .venv && . .venv/bin/activate   # Python 3.12 (3.14 may lack dep wheels)
pip install .                                        # NON-editable — see the gotcha below
openspace --help                                     # verify the REAL package (headless CLI)
```
**⚠️ Do NOT use `pip install -e .` (editable) — verified broken 2026-07-20.** The PEP 660 editable
finder leaves `import openspace` as a namespace package (`__file__=None`) and the CLI dies with
`ModuleNotFoundError`. A plain non-editable `pip install .` (or `pip install --no-deps
--force-reinstall .`) maps the package correctly and the CLI works.

**⚠️ The default `--tui` / `--doctor` path needs a built Node TUI artifact that isn't shipped** —
run **headless** with `openspace --no-ui --query "<task>"`. Set `OPENSPACE_LLM_API_KEY` +
`OPENSPACE_MODEL` (litellm ids, e.g. `anthropic/claude-sonnet-4-5`). No cloud login needed for the
local-first run+evolve path (supply-chain: self-host, pin deps, read before run).

## Trial protocol (local-first)
1. Register this repo's skills (see `INVENTORY.md`) into OpenSpace.
2. Run **3 representative real tasks** through the OpenSpace harness → it emits quality records.
3. Inspect quality: selected / applied / completed / fell-back per skill; any tool-reliability flags.
4. Trigger controlled evolution on the weakest skill; confirm **provisional→trusted** + validate-before-replace.
5. Measure vs baseline: task success, tokens/task, latency, context size.

## Success criteria (trial PASSED iff)
- Quality records for ≥3 real tasks (evidence, not vibes).
- ≥1 skill correctly flagged good-vs-weak, matching your judgment.
- Evolution produced a **validated** improvement with **no regression** on a passing task.
- Tokens/latency **not worse** (no bloat/slowdown) — record the numbers.
- Verdict: adopt / trial-more / drop + the single number that decides it.

## Feed results back
Into AnyAgent `report` cards + the fleet usage layer. Sequence: prove ONE repo before fleet-wide.
