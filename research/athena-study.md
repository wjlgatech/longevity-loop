# ATHENA-R1 — Repo Study

Study of **https://github.com/mims-harvard/ATHENA** (Marinka Zitnik's lab, Harvard).
Every claim below is cited to a file/line in the cloned repo (commit at `pushed_at`
2026-07-17) or to repo metadata. Where I could not verify something, it is flagged
**[UNVERIFIED]**.

Repo metadata (GitHub API, fetched 2026-07-18):
- Description: "ATHENA-R1: AI agent for treatment reasoning over a biomedical tool universe"
- Stars: **56**, Forks: **11**, Open issues: **0**
- Created: 2026-05-26; last push: 2026-07-17 (actively developed, ~2 months old)
- License: **MIT** (`LICENSE`, "Copyright (c) 2025 Artificial Intelligence for Medicine and Science @ Harvard")
- Package name: `athena-r1`, import `athena_r1` (`src/athena_r1/`)

---

## 1. What it is

ATHENA-R1 is an **AI agent for biomedical treatment reasoning**, trained via
reinforcement learning to do multi-step reasoning over a library of **212
biomedical tools** served through [ToolUniverse](https://github.com/mims-harvard/ToolUniverse)
(`README.md:11-17`). Rather than answering in one shot, it identifies what
evidence it needs, retrieves tools, calls them (FDA labels, OpenTargets, ChEMBL,
EuropePMC, Monarch, etc.), and folds the results into subsequent reasoning to
reach evidence-grounded clinical decisions. The shipped artifact is a fine-tuned
`Qwen3-8B` model plus a thin Python engine that orchestrates the tool-calling
loop. Maturity: young but polished research release — MIT-licensed, 56 stars, a
real test suite (~35 test files), CI (`.github/workflows/test.yml`), pre-commit,
`pyproject.toml`, two deployable web servers, and published benchmark numbers.
Explicitly **"not a medical device"** — a research artifact (`README.md:272-276`).

Key facts:
- Headline eval (`docs/eval_results.md`): DrugPC 94.7% and TreatmentPC 82.9%,
  beating GPT-5 (+17.8 / +10.7), DeepSeek-R1-671B, and Qwen3.
- Two-stage eval protocol: free-form `answer()` then a separate `map_to_option()`
  letter-mapping, "to avoid contaminating the reasoning trace" (`README.md:118-138`).
- Not stdlib-light: runtime deps are `openai, transformers, tooluniverse, jinja2,
  numpy, torch>=2.0` (`requirements.txt`), plus vLLM for serving.

---

## 2. Architecture

The core abstraction is a **multi-step tool-reasoning loop over an LLM + a tool
universe**, with a clean public wrapper hiding a large internal engine.

Layers:
- **`AthenaR1`** (`src/athena_r1/agent.py`) — the public API. Dataclasses
  `AnswerResult` and `RoundEvent`, a `Backend` enum (`ATHENA` local vLLM vs `GPT`
  Azure), and methods `answer()`, `answer_streaming()`, `map_to_option()`,
  `generate_report()`, `init()/close()`, `info()`. It validates config, sets the
  paper-canonical tool categories, and wraps everything else.
- **`AthenaCore`** (`src/athena_r1/_core.py`, ~2160 lines) — the engine. Owns the
  vLLM client, the tokenizer + Jinja2 chat template, ToolUniverse handle, and the
  `run_multistep_agent()` round loop (`_core.py:1479+`). Marked module-private;
  users are told to use `AthenaR1` (`_core.py:393-399`).
- **`AgentRunContext`** (`_core.py:28-390`) — per-run state object (conversation,
  picked tools, cancel event, progress callback) used as a context manager. Holds
  the context-compaction logic and the `_emit()` streaming event helper.
- **Tool dispatch** (`src/athena_r1/tool_processors.py`) — a small strategy-pattern
  registry (see §3).
- **Prompts** (`src/athena_r1/_prompts.py`) — three system prompts kept at module
  scope so they can be diffed/reviewed in isolation (`_prompts.py:1-9`).
- **Report** (`src/athena_r1/_report.py`) — pure, no-network digest + citation
  scaffolding for the clinical report feature (see §3).
- **Web** (`web/agui_server.py`, `web/openai_server.py`, `web/docker-compose.yml`)
  — an AG-UI protocol server and an OpenAI-compatible HTTP server, "0 code to
  write" (`README.md:167-185`).
- **Serving scripts** (`scripts/launch_*.sh`) — one-shot launchers for
  ToolUniverse + vLLM + the two servers.

Data flow of one question: `answer()` wraps the question in a paper-canonical
template (`agent.py:345-349`) → `run_multistep_agent()` loops up to `max_round`
(default 40): each round generates model output, parses `<tool_call>` blocks,
dispatches them, appends tool results, checks for `[FinalAnswer]`, and enforces
context-space budgets. Termination is via a `Finish` tool, a `[FinalAnswer]`
marker, `max_round` force-finish, or a wall-clock timeout.

---

## 3. Agentic tooling (the focus)

### Tools: how they are defined, registered, described
- Tools are **not defined in this repo** — they live in the external
  **ToolUniverse** package/server. ATHENA loads a paper-canonical category set:
  `tool_finder, opentarget, fda_drug_label, special_tools, monarch,
  fda_drug_adverse_event, ChEMBL, EuropePMC, semantic_scholar, pubtator, EFO`
  (`agent.py:249-262`). Loaded via `tooluniverse.load_tools(tool_type=...)`
  (`_core.py:579-585`).
- Tool **schemas/prompts come from ToolUniverse**: `tooluniverse.tool_specification(name,
  return_prompt=True)` returns the prompt form, and `prepare_tool_prompts(new_tools)`
  formats retrieved specs (`_core.py:624, 639-653`; `tool_processors.py:150`).
  So the schema/registry is delegated, not local.
- The model emits tools as inline text: `<tool_call>{"name": ..., "arguments":
  {...}}</tool_call>` blocks parsed by regex (`agent.py:33`) and by
  `tooluniverse.extract_function_call_json(...)` (`_core.py:739, 1285`).

### The tool-call dispatch: a strategy-pattern registry (the standout pattern)
`tool_processors.py` defines an abstract `ToolCallProcessor` with `can_handle(name)`
+ `process(tool_call, context) -> (result_str, context_updates)`. Concrete
processors, tried in order by `ToolProcessorRegistry` (`tool_processors.py:362-381`):
1. `FinishToolProcessor` — stops the loop.
2. `DirectResponseToolProcessor` — returns a direct answer (note the deliberate
   `respose` misspelling kept because the model emits it, `tool_processors.py:56-64`).
3. `RequireClarificationToolProcessor` — asks the user to clarify.
4. `ToolRAGProcessor` — the meta-tool `Tool_RAG` that **retrieves more tools at
   runtime** (`tool_processors.py:79-197`).
5. `CallAgentProcessor` — spawns a recursive child agent (§multi-agent).
6. `DefaultToolProcessor` — catch-all: executes any named ToolUniverse function
   (`tool_processors.py:345-359`). Must be last.

The five "special" names are **meta-tools / infrastructure**, hidden from
`tools_used` accounting via `_META_TOOLS` (`agent.py:730-732`).

### Skills / plugins / MCP
- **No SKILL.md-style progressive-disclosure skills.** None found.
- **No MCP server or interface.** No `mcp` imports or servers; the interoperability
  surface is instead **AG-UI protocol** (`web/agui_server.py`) and an
  **OpenAI-compatible API** (`web/openai_server.py`) (`README.md:167-185`).
- **"Plugins" = the processor registry** above: pluggable modules keyed by
  `can_handle`. That is the closest thing to a plugin system.

### Workflows / pipelines / DAGs
- **No YAML/graph workflow engine.** Orchestration is **imperative Python**: the
  `run_multistep_agent()` round loop (`_core.py:1526+`). Multi-step "pipeline" is
  the round loop + `Tool_RAG` (retrieve tools) + `CallAgent` (recurse) primitives,
  not a declarative DAG.
- There *is* a declarative **two-stage eval pipeline** by convention:
  Stage-1 `answer()` → Stage-2 `map_to_option()` (`agent.py`, `examples/eval_mcq.py`),
  and a Stage-3 `generate_report()`.

### Memory
- **No long-term / cross-session memory.** State is the per-run `conversation` list
  inside `AgentRunContext`. What exists is **context-window management** (`_core.py`):
  - Strategy 1 — preemptive compaction: `ensure_context_space()` +
    `_condense_massive_tools()` (summarize any tool output > 30% of budget) +
    `_iteratively_compress_tools()` (largest-first until under a safe limit)
    (`_core.py:97-228`).
  - Strategy 2 — reactive "context checkpoint": summarize the whole run into a
    handoff message and rebuild the conversation (`_core.py:245-278`).
  - `_emergency_final_answer()` — a 4-tier fallback that *always* returns a
    non-error answer (truncate tools → drop tools → direct answer → honest
    "couldn't verify" message) (`_core.py:311-390`).

### Verification / evaluation / evidence (strong here)
- **Citation gating in reports** (`_report.py`) is the most transferable evidence
  pattern. `assemble_digest()` emits an explicit allow-list line — `SOURCES
  AVAILABLE FOR CITATION (cite ONLY these): [...]` — built only from tools actually
  called this run (`_report.py:177-188`). `valid_source_labels()` parses that
  allow-list (`_report.py:191-197`), and `_polish_report()` **strips any citation
  the model invents** that isn't in the run's trace (`_report.py:302-347`). Raw
  function names are rewritten to human labels; the model "cannot fabricate a
  reference" (`README.md:161-165`). This is a concrete **"no evidence ⇒ no claim"**
  enforcement, implemented post-hoc with regex on stdlib `re`.
- **Tool accounting**: `_extract_tools_used()` dedupes real tools and excludes
  meta-tools (`agent.py:734-749`).
- **Evaluation**: two-stage open-ended protocol with two independent mappers
  (self-extraction vs GPT-5), deliberately separated to avoid trace contamination
  (`README.md:135-138`, `examples/eval_mcq.py`).

### Tool selection
- **Retrieval-augmented tool selection (`Tool_RAG`)**: instead of stuffing all 212
  tool schemas into the prompt, the agent calls `Tool_RAG` with a natural-language
  description and gets back the top-k relevant tool specs (default `step_rag_num=5`),
  which are appended to the live tool prompt (`agent.py:149,193-194`;
  `tool_processors.py:89-187`). Backed by a retrieval model
  `mims-harvard/ToolRAG-T1-GTE-Qwen2-1.5B` (`agent.py:149`).

### Multi-agent coordination
- **Recursive sub-agents via `CallAgent`** (`tool_processors.py:200-342`). A parent
  can spawn a child that runs its own `run_multistep_agent()`; children get ids like
  `main.sub-1`, `main.sub-1.sub-1`; depth gated by `max_agent_level` (default 0 =
  off). **Consecutive `CallAgent` calls run in parallel** via a `ThreadPoolExecutor`
  capped at 4 (`_core.py:807-865`), with results committed back in original order.
  Cancellation propagates to children through a shared `cancel_event`
  (`tool_processors.py:311-314`).

### Reproducibility / gating / provenance
- **Makefile targets** split offline vs full tests: `make test-offline` (no
  vLLM/TU needed), `make test-full`, `make repro` (`Makefile`).
- **Resumable reproduction harness**: `tests/test_reproducibility_full.py` runs the
  full 456-question TreatmentPC set, appending per-question JSONL progress so a run
  is resumable, with a per-question wall-clock cap (`test_reproducibility_full.py:1-45`).
- **Pinned inference settings** documented as a table for reproducibility
  (`docs/eval_results.md:54-62`); env-var overrides for ablations
  (`INFER_PRESENCE_PENALTY`, etc., `_core.py:924-929`).
- **Held-out data to avoid leakage**: FDA-2024-approved drugs excluded from training
  (`docs/eval_results.md:11-12`).
- **CI**: `.github/workflows/test.yml`; `.pre-commit-config.yaml`; ruff lint/format.
- The MCQ dataset is intentionally **not redistributed** (`test_reproducibility_full.py:30-33`).

---

## 4. The 3–5 best, transferable ideas (ranked)

1. **Trace-scoped citation allow-list ("no evidence ⇒ no claim", enforced in code).**
   Build an allow-list of sources from what the agent *actually retrieved this run*,
   pass it into the writer, then **programmatically strip any citation not in the
   allow-list** (`_report.py:177-347`). Pure stdlib `re`, post-hoc, model-agnostic.
   This is the single most valuable idea and maps 1:1 onto an evidence-gated repo.

2. **Strategy-pattern tool/handler registry with `can_handle` + ordered fallthrough.**
   Each capability is a small class with a predicate and a `process()` returning
   `(result, context_updates)`; a registry tries them in order with a catch-all last
   (`tool_processors.py`). Trivial to extend, easy to test in isolation, no
   framework. A clean way to structure any "route input to the right handler" agent.

3. **Retrieval-augmented tool/capability selection (`Tool_RAG`).**
   Don't put every capability in the prompt/registry up front — retrieve the top-k
   relevant ones on demand from a large library (`tool_processors.py:79-197`). Keeps
   context small and scales to hundreds of tools.

4. **Graceful, tiered degradation that never returns a raw error.**
   `_emergency_final_answer()`'s 4-tier fallback and the two-strategy context
   compaction (`_core.py:97-390`) guarantee a useful, honest output under failure,
   ending with an explicit "I couldn't verify this" rather than a stack trace.

5. **Separation of reasoning from scoring, + resumable/pinned reproduction.**
   Stage-1 free-form answer kept *separate* from Stage-2 letter-mapping to avoid
   contaminating the trace (`README.md:135-138`); reproduction harness is resumable
   (JSONL checkpoint) with pinned settings and held-out data
   (`test_reproducibility_full.py`, `docs/eval_results.md`).

---

## 5. Adoptability for `longevity-loop`

Target = solo, stdlib-Python, dependency-light (pyyaml only in core), `data/*.yml`
as single source of truth, generator scripts render docs, `make check`
(validate + audit + eval + drift) enforces "no evidence ⇒ no claim". Existing small
agentic scripts (frontier tracker, Europe-PMC synthesizer, clock-disagreement
benchmark, FAIR scorecard, daily recap).

| ATHENA idea | Port to longevity-loop? | Why |
|---|---|---|
| **1. Trace-scoped citation allow-list** | **YES — highest value** | Pure `re`/stdlib, no deps. Build the allow-list from `data/*.yml` source IDs (PMIDs/DOIs), have any generator/synthesizer emit only those, and add a `make check` step that strips/flags citations not in the allow-list. This *is* your "no evidence ⇒ no claim" gate, made mechanical. |
| **2. Strategy-pattern handler registry** | **YES (lightweight)** | ~40 lines of stdlib. If your agentic scripts have grown `if source == ...` branches (Europe-PMC vs frontier vs clocks), a `can_handle`/`process` registry cleans them up and makes each handler unit-testable. Adopt only where branching already hurts; don't over-engineer a single-source script. |
| **4. Tiered graceful degradation + honest "couldn't verify"** | **YES (partial)** | The *principle* ports cheaply: each script should return a structured "insufficient evidence" result instead of crashing or fabricating, and the recap/scorecard should surface it. Skip the model-summarization tiers (needs an LLM) — just adopt the honest-fallback discipline. |
| **5. Reasoning/scoring separation + resumable, pinned eval** | **YES (partial)** | Your clock-disagreement benchmark and FAIR scorecard can copy the JSONL-checkpoint-resumable pattern and a pinned-settings table (stdlib `json`). Keep "generate" separate from "score/gate" — matches your validate/audit/eval split already. |
| **3. Retrieval-augmented tool selection (`Tool_RAG`)** | **NO / overkill** | Needs an embedding model + retriever + a large tool library. You have a handful of scripts and a YAML SoT; a static list/dispatch is simpler and sufficient. |
| Multi-agent `CallAgent` recursion + parallel subagents | **NO / overkill** | ThreadPool subagent orchestration is heavy research infra for a solo, deterministic, code-only repo. A plain function call or a sequenced generator does the job. |
| ToolUniverse dependency, vLLM serving, AG-UI/OpenAI web servers | **NO** | Contradicts the stdlib/dependency-light constraint and the "render to docs" model. Not applicable. |
| Context-window compaction (Strategy 1/2) | **NO** | Only matters for long live LLM traces; irrelevant to a YAML-driven generator pipeline. |

**Bottom line for longevity-loop:** take ideas **1, 2, 4, 5** — all implementable in
stdlib Python and directly reinforcing the existing `make check` "no evidence ⇒ no
claim" contract. The citation allow-list (idea 1) is the highest-leverage, near-drop-in
adoption. Everything tied to ToolUniverse, vLLM, RAG retrieval, or multi-agent
recursion is heavy research infrastructure that does not fit a solo, low-dependency,
data-driven repo.
