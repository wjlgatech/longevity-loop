# Repo hub — generation recipes (RECIPE layer)

_Generated from `data/stack.yml` + `data/frontier.yml` by `scripts/repos.py`. See the design in [HUB_ARCHITECTURE.md](HUB_ARCHITECTURE.md)._

**22 cited repos** (20 on GitHub). This is the **recipe**, not the artifacts: run a repo's commands **on demand** and cache the result by the repo's commit SHA — deep knowledge graphs and skills are made just-in-time, never committed stale. You never pay for a repo you don't use.

## The recipe (per repo)

```bash
# 1. knowledge graph
understand-anything <clone-dir>     # GitHub codebases (architecture KG)
graphify <url>                      # model cards / docs / papers (clustered KG)
# 2. agentic tooling (skill / plugin / workflow)
anyagent reverse <url> --markdown  # → blueprint, then:
anyagent build/refine "<blueprint>" --target-score 80   # → a gated skill/workflow
# 3. serve to any client
anyagent mcp                       # expose the generated tools over MCP
```

> Quality gate: stamp every generated artifact with the source repo + commit SHA (reproducible + staleness-detectable); a skill ships only after `refine` clears its score.

## The repos

| Repo | Kind | Host | KG engine | Tooling |
|---|---|---|---|---|
| [BixBench](https://github.com/Future-House/BixBench) | benchmark | github | `understand-anything` | `anyagent reverse Future-House/BixBench` |
| [LAB-Bench](https://github.com/Future-House/LAB-Bench) | benchmark | github | `understand-anything` | `anyagent reverse Future-House/LAB-Bench` |
| [Open Problems in Single-Cell](https://github.com/openproblems-bio/openproblems) | benchmark | github | `understand-anything` | `anyagent reverse openproblems-bio/openproblems` |
| [DunedinPACE](https://github.com/danbelsky/DunedinPACE) | clock | github | `understand-anything` | `anyagent reverse danbelsky/DunedinPACE` |
| [scAge](https://github.com/alex-trapp/scAge) | clock | github | `understand-anything` | `anyagent reverse alex-trapp/scAge` |
| [Marinka Zitnik](https://github.com/mims-harvard/ATHENA) | frontier-work | github | `understand-anything` | `anyagent reverse mims-harvard/ATHENA` |
| [Morgan Levine](https://github.com/HigginsChenLab/methylCIPHER) | frontier-work | github | `understand-anything` | `anyagent reverse HigginsChenLab/methylCIPHER` |
| [cognee](https://github.com/topoteretes/cognee) | graph | github | `understand-anything` | `anyagent reverse topoteretes/cognee` |
| [Graphiti](https://github.com/getzep/graphiti) | graph | github | `understand-anything` | `anyagent reverse getzep/graphiti` |
| [PyTorch Geometric Temporal](https://github.com/benedekrozemberczki/pytorch_geometric_temporal) | graph | github | `understand-anything` | `anyagent reverse benedekrozemberczki/pytorch_geometric_temporal` |
| [TGB (Temporal Graph Benchmark)](https://github.com/shenyangHuang/TGB) | graph | github | `understand-anything` | `anyagent reverse shenyangHuang/TGB` |
| [AltumAge](https://github.com/rsinghlab/AltumAge) | model | github | `understand-anything` | `anyagent reverse rsinghlab/AltumAge` |
| [ESM-2](https://github.com/facebookresearch/esm) | model | github | `understand-anything` | `anyagent reverse facebookresearch/esm` |
| [Geneformer](https://huggingface.co/ctheodoris/Geneformer) | model | huggingface | `graphify` | `anyagent reverse <url>` |
| [scGPT](https://github.com/bowang-lab/scGPT) | model | github | `understand-anything` | `anyagent reverse bowang-lab/scGPT` |
| [TxGNN](https://github.com/mims-harvard/TxGNN) | model | github | `understand-anything` | `anyagent reverse mims-harvard/TxGNN` |
| [AlphaFold](https://github.com/google-deepmind/alphafold) | tool | github | `understand-anything` | `anyagent reverse google-deepmind/alphafold` |
| [Biolearn](https://bio-learn.github.io/) | tool | web | `graphify` | `anyagent reverse <url>` |
| [CZ CELLxGENE Census](https://github.com/chanzuckerberg/cellxgene-census) | tool | github | `understand-anything` | `anyagent reverse chanzuckerberg/cellxgene-census` |
| [pyaging](https://github.com/rsinghlab/pyaging) | tool | github | `understand-anything` | `anyagent reverse rsinghlab/pyaging` |
| [scanpy](https://github.com/scverse/scanpy) | tool | github | `understand-anything` | `anyagent reverse scverse/scanpy` |
| [ToolUniverse](https://github.com/mims-harvard/ToolUniverse) | tool | github | `understand-anything` | `anyagent reverse mims-harvard/ToolUniverse` |

---

KG engine split: `understand-anything` for the 20 GitHub codebases, `graphify` for model cards / docs. PR a repo into `data/stack.yml` and it joins the hub automatically.
