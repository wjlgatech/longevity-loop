#!/usr/bin/env python3
"""repos — the hub's RECIPE layer (docs/HUB_ARCHITECTURE.md, Phase 0).

Turns the registry (data/stack.yml + repo links in data/frontier.yml) into a per-repo
**generation recipe**: for each cited repo, the exact command to build its knowledge graph
and to reverse its agentic tooling — deterministically, from the single source of truth.

It deliberately generates NO knowledge graphs or skills here: those are expensive and go
stale, so they're made just-in-time (cached by commit SHA), not committed. This layer is
the cheap, always-fresh index of *how* to make them — see docs/HUB_ARCHITECTURE.md.

  repos.py            # write docs/REPOS.md
  repos.py --check    # compare instead of writing (drift gate, like build.py --check)
  repos.py --selftest # assert classification behaves
"""
from __future__ import annotations

import re
import sys
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "docs" / "REPOS.md"


def load(name: str):
    p = DATA / f"{name}.yml"
    return (yaml.safe_load(p.read_text()) if p.exists() else []) or []


def classify(url: str) -> tuple[str, str]:
    """(host, kg_engine) for a repo URL. github codebases → understand-anything;
    model cards / docs / papers → graphify."""
    u = (url or "").lower()
    if "github.com/" in u:
        return "github", "understand-anything"
    if "huggingface.co/" in u:
        return "huggingface", "graphify"
    return "web", "graphify"


def slug(url: str) -> str:
    m = re.search(r"github\.com/([^/]+/[^/#?]+)", url or "")
    return m.group(1).rstrip("/") if m else "-"


def collect() -> list[dict]:
    """Cited repos from the stack (models/tools/clocks/datasets/benchmarks) + frontier
    works that point at a repo. Deduped by URL; only real, generatable sources."""
    seen, out = set(), []
    for x in load("stack"):
        url = x.get("url", "")
        if not url or url in seen:
            continue
        host, engine = classify(url)
        if host == "web" and "github" not in url and "huggingface" not in url:
            continue  # a plain website (e.g. a portal) isn't a generatable repo — skip
        seen.add(url)
        out.append({"name": x.get("name", ""), "kind": x.get("kind", "tool"),
                    "url": url, "host": host, "engine": engine, "slug": slug(url)})
    for f in load("frontier"):
        url = f.get("repo", "")
        if url and url != "-" and url not in seen and ("github.com" in url or "huggingface.co" in url):
            seen.add(url)
            host, engine = classify(url)
            out.append({"name": f.get("name", ""), "kind": "frontier-work",
                        "url": url, "host": host, "engine": engine, "slug": slug(url)})
    return out


def render() -> str:
    repos = collect()
    by_engine = {}
    for r in repos:
        by_engine.setdefault(r["engine"], []).append(r)
    gh = sum(1 for r in repos if r["host"] == "github")
    L = [
        "# Repo hub — generation recipes (RECIPE layer)", "",
        "_Generated from `data/stack.yml` + `data/frontier.yml` by `scripts/repos.py`. See the "
        "design in [HUB_ARCHITECTURE.md](HUB_ARCHITECTURE.md)._", "",
        f"**{len(repos)} cited repos** ({gh} on GitHub). This is the **recipe**, not the artifacts: "
        "run a repo's commands **on demand** and cache the result by the repo's commit SHA — deep "
        "knowledge graphs and skills are made just-in-time, never committed stale. You never pay for "
        "a repo you don't use.", "",
        "## The recipe (per repo)", "",
        "```bash",
        "# 1. knowledge graph",
        "understand-anything <clone-dir>     # GitHub codebases (architecture KG)",
        "graphify <url>                      # model cards / docs / papers (clustered KG)",
        "# 2. agentic tooling (skill / plugin / workflow)",
        "anyagent reverse <url> --markdown  # → blueprint, then:",
        "anyagent build/refine \"<blueprint>\" --target-score 80   # → a gated skill/workflow",
        "# 3. serve to any client",
        "anyagent mcp                       # expose the generated tools over MCP",
        "```", "",
        "> Quality gate: stamp every generated artifact with the source repo + commit SHA "
        "(reproducible + staleness-detectable); a skill ships only after `refine` clears its score.", "",
        "## The repos", "",
        "| Repo | Kind | Host | KG engine | Tooling |",
        "|---|---|---|---|---|",
    ]
    for r in sorted(repos, key=lambda r: (r["kind"], r["name"].lower())):
        tooling = f"`anyagent reverse {r['slug']}`" if r["host"] == "github" else "`anyagent reverse <url>`"
        L.append(f"| [{r['name']}]({r['url']}) | {r['kind']} | {r['host']} | `{r['engine']}` | {tooling} |")
    L += ["", "---", "",
          f"KG engine split: `understand-anything` for the {gh} GitHub codebases, `graphify` for "
          "model cards / docs. PR a repo into `data/stack.yml` and it joins the hub automatically.", ""]
    return "\n".join(L)


def selftest() -> int:
    assert classify("https://github.com/bowang-lab/scGPT")[0] == "github"
    assert classify("https://github.com/bowang-lab/scGPT")[1] == "understand-anything"
    assert classify("https://huggingface.co/ctheodoris/Geneformer")[1] == "graphify"
    assert slug("https://github.com/rsinghlab/pyaging") == "rsinghlab/pyaging"
    assert collect(), "expected ≥1 cited repo from stack.yml"
    print(f"repos selftest: OK (classification + slug; {len(collect())} repos collected).")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    text = render()
    if "--check" in sys.argv:
        current = OUT.read_text() if OUT.exists() else ""
        if current != text:
            print("Out of date: docs/REPOS.md. Run `make repos`.", file=sys.stderr)
            return 1
        print("docs/REPOS.md is up to date.")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text)
    print(f"Wrote {OUT.relative_to(ROOT)} — {len(collect())} repos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
