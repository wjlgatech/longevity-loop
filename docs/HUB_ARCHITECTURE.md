# The hub architecture — knowledge · tooling · experts, per cited repo

_How this repo becomes the **hub** that offers, for each top cited repo, a **knowledge graph**
(knowledge) and **agentic tooling** (skills / plugins / workflows) — engineered to be high-quality,
fast, cheap, always up-to-date, and future-proof._

---

## The one decision that determines everything: INDEX + JIT, not a warehouse of frozen artifacts

The tempting move — eagerly generate and commit a KG + a skill + a plugin + a workflow for all ~27
cited repos — is the wrong one, and it fails **every** quality bar at once:

| Bar | Why the "generate-all-now" approach fails it |
|---|---|
| High quality | Bulk auto-generation is slop — 27 repos × 4 artifacts, none verified against the real repo. |
| Fast | Serial LLM generation over 100+ artifacts is slow to produce and slow to review. |
| Cheap | You pay LLM cost for every repo × every artifact, including repos no one ever uses. |
| Up-to-date | Repos push weekly; a committed KG/skill is **stale the day after** you generate it. |
| Future-proof | A frozen pile of bespoke artifacts is a maintenance graveyard, not an asset. |

So the architecture is three layers, each optimized for a different bar:

```
① INDEX  (committed, cheap, always fresh)   ── the hub's front door
   registry (data/stack.yml) + live GitHub metadata → a ranked, queryable repo index
        │  (cheap: API only, no LLM · fresh: weekly cron · deterministic)
        ▼
② RECIPE (committed, deterministic)          ── how to make the deep artifacts, per repo
   per-repo generation commands: KG via graphify/understand-anything · tooling via anyagent reverse
        │  (this file's PoC: scripts/repos.py → docs/REPOS.md)
        ▼
③ JIT DEEP (generated on demand, cached by commit SHA, NOT committed) ── the actual KG + skills
   run the recipe only when you need a repo, cache it, regenerate only when the repo's SHA changes
        │  (quality: verified/gated · cheap: never for an unused repo · fresh: SHA-keyed)
        ▼
④ INTEROP (MCP + portable formats)           ── future-proof
   KGs as JSON · skills as SKILL.md · tools via `anyagent mcp` → any agent client can consume the hub
```

**The thesis in one line:** keep a *fresh, cheap index* committed; generate the *expensive deep
artifacts just-in-time* by reusing existing engines, keyed to the source commit so they're never
stale — you never pay for a repo you don't use, and you never ship one that's out of date.

---

## Reuse the engines — don't rebuild them (backbone: *call it, don't absorb it*)

Every deep artifact maps to a tool that already exists. The hub **orchestrates**; it does not
reimplement graph extraction or skill synthesis.

| Deep artifact | Engine to reuse | Input |
|---|---|---|
| Knowledge graph (codebase) | `understand-anything` (code → architecture KG) | a cloned repo |
| Knowledge graph (docs/model card/paper) | `graphify` (any input → clustered KG + HTML/JSON) | README / model card / paper |
| Agentic tooling blueprint | `anyagent reverse <repo> --markdown` | repo URL |
| Skill / workflow from that blueprint | `anyagent build` / `refine` (gated to a score) | the blueprint |
| Serve it to any client | `anyagent mcp` (MCP) / a `SKILL.md` | the generated tool |
| Live repo metadata | GitHub API (already in `scripts/track.py`) | the repo slug |

If a better KG engine appears, you swap the **recipe**, not the data — that's the future-proofing.

---

## How each quality bar is met

- **High quality** — *no evidence ⇒ no claim* applied to generation: each artifact records the source
  repo + **commit SHA** it was built from, and a skill only ships if `anyagent refine` clears its
  score gate (does it build? does it run?). Provenance = reproducible + drift-detectable.
- **Fast** — the index is API-only (seconds); deep generation fans out **per-repo in parallel**
  (subagents / a workflow), and only for repos you asked for or that changed.
- **Cheap** — zero LLM in the index. LLM only in ③, only JIT, only when the SHA moved. An unchanged
  repo is never regenerated; an unused repo is never generated at all.
- **Up-to-date** — the weekly cron (extend `track.yml`) refreshes ① and stamps each deep artifact with
  its source SHA; when the repo moves, the artifact is flagged **stale**, not silently wrong.
- **Future-proof** — portable standard formats (JSON KG, `SKILL.md`, MCP), registry-driven from the
  single source of truth (`data/stack.yml`), swappable engines. The hub is MCP-queryable, so any
  future client (Claude Desktop/Code, another agent) consumes it without bespoke glue.

## The third pillar — experts — is already wired

`people.yml` + `frontier.yml` + the bi-temporal field graph (`build_graph.py`) already link
experts ↔ orgs ↔ topics ↔ recent works. The hub adds the missing edge: **repo → maintainer/lab →
expert**, so "knowledge (KG) · tooling (skills) · experts (people)" become one graph you can traverse
(e.g. *pyaging → rsinghlab → the clocks experts to reach*).

---

## Phased rollout (decompose — never one-shot)

- **Phase 0 (this PR):** the RECIPE layer — `scripts/repos.py` turns `data/stack.yml` into a per-repo
  generation index (`docs/REPOS.md`): KG command + tooling command + provenance, deterministic and
  gated. Proves the model with **zero** wasteful generation.
- **Phase 1:** enrich ① with live GitHub metadata (stars, last-push SHA, license, health) on the
  weekly cron — extend `track.py`; write a generated `data/_repos.yml` (like `_frontier.yml`).
- **Phase 2:** JIT deep generation for the **top-N** repos only (start with the North-Star lane:
  Biolearn, pyaging, Geneformer, scGPT), via `graphify` + `anyagent reverse`, cached by SHA, exposed
  via MCP. Verified/gated before publish.
- **Phase 3:** surface the hub in the agentic-portfolio instance (reads the same `tracker.json` +
  `_repos.yml`), so the KG/tooling/experts hub is browsable and agent-answerable.

**Anti-pattern to avoid at every phase:** committing a deep artifact without its source SHA, or
generating for a repo before someone needs it. Fresh index, lazy depth.

_Not medical advice. All artifacts are computational metadata about open-source repos; no wet-lab or
therapeutic claim._
