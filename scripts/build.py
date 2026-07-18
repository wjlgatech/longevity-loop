#!/usr/bin/env python3
"""Render README.md + docs/ROADMAP.md from data/*.yml — the single source of truth.

Never hand-edit the generated files; edit data/*.yml and run `make build`
(CI drift-gates them). This is the same spec-as-data discipline as FM-os.
"""
from __future__ import annotations

import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
README = ROOT / "README.md"
ROADMAP = ROOT / "docs" / "ROADMAP.md"
NULLS = ROOT / "docs" / "NULLS.md"
BADGE = "https://img.shields.io/github"


def load(name: str):
    p = DATA / f"{name}.yml"
    return (yaml.safe_load(p.read_text()) if p.exists() else []) or []


def esc(t: object) -> str:
    return " ".join(str("" if t is None else t).split())


def render_readme() -> str:
    meta, loop, road = load("meta"), load("loop"), load("roadmap")
    people, startups, stack, eco = load("people"), load("startups"), load("stack"), load("ecosystem")
    turns, frontier, reflections = load("turns"), load("frontier"), load("reflections")
    execs = load("executions")
    nulls = load("nulls")
    datasets = load("datasets")
    slug = f"{meta['repo_owner']}/{meta['repo_name']}"
    L: list[str] = []

    L += [
        f"# {meta['title']}", "",
        "<div align=\"center\">", "",
        f"[![CI]({BADGE}/actions/workflow/status/{slug}/ci.yml?style=flat-square&label=loop%20check)](https://github.com/{slug}/actions)",
        f"[![Last Updated]({BADGE}/last-commit/{slug}?style=flat-square&label=last%20turn)](https://github.com/{slug}/commits/main)",
        f"[![License]({BADGE}/license/{slug}?style=flat-square)](LICENSE)", "",
        esc(meta["sibling_banner"]), "",
        esc(meta["tagline"]), "",
        esc(meta["north_star"]), "",
        "</div>", "", "---", "",
        f"> {esc(meta['disclaimer'])}", "", "---", "",
    ]

    # The loop
    L += ['<h2 id="the-loop">♻️ The Loop (one turn of the flywheel)</h2>', "",
          "Each turn is falsifiable and ends in a shared, verifiable artifact. No evidence ⇒ no claim.", "",
          "| # | Stage | What happens |", "|--:|---|---|"]
    for s in loop["stages"]:
        L.append(f"| {s['n']} | **{esc(s['name'])}** | {esc(s['do'])} |")
    L += ["", "> ⑦ COMPOUND feeds back into ① — each turn adds data, a tool, or a connection, so the next question is bigger.", "", "---", ""]

    # Turns ledger (build-in-public progress)
    icon = {"scaffolded": "🧩", "in-progress": "🔄", "done": "✅"}
    L += ['<h2 id="turns">📓 Turns Log</h2>', "",
          "Every turn of the loop, logged honestly. `done` requires a PROOF (result incl. the null + a reproduce command).", "",
          "| Turn | Question | Stage | Status |", "|---|---|---|:--|"]
    for t in turns:
        L.append(f"| [{esc(t['id'])}]({t['path']}) | {esc(t['question'])} | {esc(t['stage'])} | {icon.get(t['status'],'')} {esc(t['status'])} |")
    L += ["", "---", ""]

    # Frontier Radar (individual recent works) + congregational graph
    if frontier:
        L += ['<h2 id="frontier">🛰️ Frontier Radar</h2>', "",
              "The frontier groundbreakers' most recent deep works — verified, with a link + a real "
              "quote. Refreshed weekly by [`scripts/track.py`](scripts/track.py) (arXiv + GitHub).", ""]
        for f in frontier:
            link = f"[{esc(f['recent_work'])}]({f['link']})" if f.get("link") and f["link"] != "-" else esc(f.get("recent_work", ""))
            L.append(f"- **{esc(f['name'])}** — {link} _({esc(f.get('year',''))})_")
            L.append(f"  {esc(f.get('summary',''))}")
            if f.get("quote") and f["quote"] != "-":
                L.append(f"  > \"{esc(f['quote'])}\"")
            if f.get("future_direction") and f["future_direction"] != "-":
                L.append(f"  → _Future:_ {esc(f['future_direction'])}")
        L += ["",
              "**🕸️ Congregational view:** the field as a spatiotemporal knowledge graph "
              "(modeled after [getzep/graphiti](https://github.com/getzep/graphiti)) — "
              "**[open the field graph →](https://wjlgatech.github.io/longevity-loop/graph.html)**.", ""]
        if reflections:
            L += ["**Reflections — what else could be important?** _(synthesis, not claims)_", ""]
            L += [f"- {esc(r)}" for r in reflections]
        L += ["", "---", ""]

    # Roadmap summary
    L += ['<h2 id="90-day-roadmap">🗺️ 90-Day Roadmap</h2>', "",
          "Three tracks every week — full weekly plan in **[docs/ROADMAP.md](docs/ROADMAP.md)**:", ""]
    L += [f"- {esc(t)}" for t in road["tracks"]]
    L += [""]
    for ph in road["phases"]:
        L += [f"### {esc(ph['title'])} · _{esc(ph['days'])}_", f"{esc(ph['theme'])}", "",
              f"**{esc(ph['milestone'])}**", ""]
    L += ["**Signal ladder** (each rung recruits the next):", ""]
    L += [f"{i}. {esc(r)}" for i, r in enumerate(road["signal_ladder"], 1)]
    L += ["", "---", ""]

    # Roadmap execution — checkbox + before→after eval
    if execs:
        done = sum(1 for e in execs if e.get("done"))
        pct = round(100 * done / len(execs))
        L += ['<h2 id="execution">✅ Roadmap Execution</h2>', "",
              f"**{done}/{len(execs)} done ({pct}%).** Each execution is a checkbox with a before→after "
              "eval; a box only ticks with a real result (`done` requires a non-pending before AND after — "
              "no evidence ⇒ not done, gated in CI).", ""]
        for e in execs:
            box = "x" if e.get("done") else " "
            L.append(f"- [{box}] **{esc(e['id'])}** ({esc(e.get('phase',''))}) — {esc(e['item'])}")
        L += ["", "### Eval reports — before → after", "",
              "| Execution | Metric | Before | After |", "|---|---|---|---|"]
        for e in execs:
            ev = e.get("eval") or {}
            mark = "✅ " if e.get("done") else "⬜ "
            L.append(f"| {mark}{esc(e['id'])} | {esc(ev.get('metric','—'))} | {esc(ev.get('before','—'))} | {esc(ev.get('after','—'))} |")
        L += ["", "---", ""]

    # Honest-nulls registry (pointer; full list in docs/NULLS.md)
    if nulls:
        L += ['<h2 id="nulls">🪦 Honest Nulls</h2>', "",
              f"**{len(nulls)} logged.** Longevity claims that failed, were refuted, or returned a clean "
              "null — recorded so the field (and this loop) stops re-learning the same failures. "
              "No evidence ⇒ no claim applies to *negatives* too. Full registry with sources: "
              "**[docs/NULLS.md](docs/NULLS.md)**.", ""]
        for n in nulls[:4]:
            L.append(f"- **[{esc(n['name'])}]({n['url']})** — _{esc(n.get('verdict',''))}_ "
                     f"({esc(n.get('year',''))}): {esc(n.get('lesson',''))}")
        L += ["", "---", ""]

    # Reproducibility / FAIR (pointer; full scorecard in docs/FAIR.md)
    if datasets:
        openn = sum(1 for d in datasets if d.get("access") == "open")
        L += ['<h2 id="fair">♻️ Reproducibility (FAIR data)</h2>', "",
              f"**{len(datasets)} open aging datasets** scored against FAIR (Findable · Accessible · "
              f"Interoperable · Reusable) — {openn} openly accessible. The field lacks shared FAIR/"
              "metadata standards for multi-omic aging data (gaps-analysis.md G2), so each dataset "
              "carries a datasheet + an honest self-assessment (unknown ⇒ no). Full scorecard with "
              "load recipes: **[docs/FAIR.md](docs/FAIR.md)**.", "", "---", ""]

    # Landscape
    L += ['<h2 id="people">🧠 Researchers</h2>', "",
          "🤖 = AI-forward · 💬 = active in the open community (good first contacts).", ""]
    for p in people:
        marks = ("🤖" if p.get("ai_forward") else "") + ("💬" if p.get("approachable") else "")
        L.append(f"- **[{esc(p['name'])}]({p['url']})** {marks} — {esc(p['org'])}: {esc(p['known_for'])}")
    L += ["", "---", "", '<h2 id="startups">🏢 Startups & Labs</h2>', "",
          "🤖 = AI-native platform.", ""]
    for s in startups:
        L.append(f"- **[{esc(s['name'])}]({s['url']})** {'🤖' if s.get('ai_native') else ''} — {esc(s['focus'])} _({esc(s.get('stage',''))})_")
    L += ["", "---", "", '<h2 id="stack">🛠️ The Buildable Stack (open, code-only)</h2>', ""]
    for kind in ("model", "tool", "clock", "dataset", "benchmark"):
        rows = [x for x in stack if x.get("kind") == kind]
        if not rows:
            continue
        L.append(f"### {kind.title()}s")
        L += [f"- **[{esc(x['name'])}]({x['url']})** — {esc(x['note'])}" for x in rows]
        L.append("")
    L += ["---", "", '<h2 id="ecosystem">🤝 Funding & Community</h2>', "",
          "✅ = realistically open to a solo/independent builder.", ""]
    for e in eco:
        L.append(f"- **[{esc(e['name'])}]({e['url']})** {'✅' if e.get('open_to_independents') else '🔒'} _{esc(e['type'])}_ — {esc(e['note'])}")
    L += ["", "---", "",
          '<h2 id="build-in-public">📣 Build in public</h2>', "",
          "This repo IS the artifact: every turn commits data, a result, or a connection. Follow the commits, "
          "open an issue with a paper/dataset/collaborator, or PR an entry to `data/*.yml`.", "",
          "<sub>Generated from <code>data/*.yml</code> by <code>scripts/build.py</code> — do not edit by hand. "
          "A sibling of <a href=\"https://github.com/wjlgatech/FM-os\">FM-os</a>.</sub>", ""]
    return "\n".join(L)


def render_roadmap() -> str:
    road = load("roadmap")
    L = ["# longevity-loop — 90-Day Roadmap", "",
         "_Generated from `data/roadmap.yml`. Three tracks every week: 🧠 Knowledge · 🛠️ Tooling · 🤝 Connections._", ""]
    for t in road["tracks"]:
        L.append(f"- {esc(t)}")
    L.append("")
    for ph in road["phases"]:
        L += [f"## {esc(ph['title'])} · {esc(ph['days'])}", "", f"_{esc(ph['theme'])}_", ""]
        for w in ph["weeks"]:
            L += [f"### Week {esc(w['week'])}",
                  f"- 🧠 **Knowledge** — {esc(w['knowledge'])}",
                  f"- 🛠️ **Tooling** — {esc(w['tooling'])}",
                  f"- 🤝 **Connections** — {esc(w['connections'])}", ""]
        L += [f"> ✅ **{esc(ph['milestone'])}**", "", "---", ""]
    return "\n".join(L)


def render_nulls() -> str:
    nulls = load("nulls")
    icon = {"refuted": "❌", "failed": "🛑", "null": "⚪", "unproven": "🟡"}
    L = ["# longevity-loop — Honest Nulls Registry", "",
         "_Generated from `data/nulls.yml` by `scripts/build.py` — do not edit by hand._", "",
         "Longevity interventions and claims that **failed, were refuted, or returned a clean null.** "
         "The field has no shared registry of honest negatives (gaps-analysis.md G4), so each "
         "generation re-learns the same failures — from Voronoff's monkey glands to resveratrol to "
         "young blood. Recording them is high-trust signal and the `no evidence ⇒ no claim` "
         "discipline applied to negatives.", "",
         "> Not medical advice. Each entry cites a public source; verdicts describe the *evidence*, "
         "not a final word on a mechanism.", "",
         "| Claim | Verdict | Class | Era | What happened | Lesson |",
         "|---|:--|---|---|---|---|"]
    for n in nulls:
        v = f"{icon.get(n.get('verdict',''),'')} {esc(n.get('verdict',''))}"
        L.append(f"| [{esc(n['name'])}]({n['url']}) | {v} | {esc(n.get('class',''))} | "
                 f"{esc(n.get('year',''))} | {esc(n.get('what_happened',''))} | {esc(n.get('lesson',''))} |")
    L += ["", "---", "",
          "PR an entry to `data/nulls.yml` (needs a real source). A clean, well-documented null is a "
          "contribution, not a failure.", ""]
    return "\n".join(L)


def main() -> int:
    outputs = {README: render_readme(), ROADMAP: render_roadmap(), NULLS: render_nulls()}
    if "--check" in sys.argv:
        stale = [p.name for p, txt in outputs.items() if (p.read_text() if p.exists() else "") != txt]
        if stale:
            print(f"Out of date: {', '.join(stale)}. Run `make build`.", file=sys.stderr)
            return 1
        print("Generated docs are up to date: " + ", ".join(p.name for p in outputs))
        return 0
    for p, txt in outputs.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(txt)
    print("Wrote " + ", ".join(p.name for p in outputs) + ".")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
