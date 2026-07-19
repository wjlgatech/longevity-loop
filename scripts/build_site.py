#!/usr/bin/env python3
"""Compile data/*.yml -> site/data.json for the build-in-public dashboard.

Same single source of truth as the README, so the live site can't drift from it.
"""
from __future__ import annotations

import json
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "site" / "data.json"
TRACKER = ROOT / "site" / "tracker.json"
SITE_BASE = "https://wjlgatech.github.io/longevity-loop"


def load(name: str):
    p = DATA / f"{name}.yml"
    return (yaml.safe_load(p.read_text()) if p.exists() else []) or []


def build_tracker(bundle: dict) -> dict:
    """A curated, stable CONTRACT for the interactive tracker (the agentic-portfolio
    instance consumes this — see research/portfolio-extension-study.md). All values are
    DERIVED from data/*.yml, so the portfolio can't drift from the loop's source of truth."""
    meta = bundle.get("meta") or {}
    repo = f"https://github.com/{meta.get('repo_owner','wjlgatech')}/{meta.get('repo_name','longevity-loop')}"
    execs = bundle.get("executions") or []
    done = [e for e in execs if e.get("done")]
    eco = bundle.get("ecosystem") or []

    return {
        "_generated": "by scripts/build_site.py from data/*.yml — do not edit; the tracker's contract.",
        "mission": {
            "title": meta.get("title", ""), "tagline": meta.get("tagline", ""),
            "north_star": meta.get("north_star", ""), "disclaimer": meta.get("disclaimer", ""),
            "repo": repo,
        },
        "progress": {"done": len(done), "total": len(execs),
                     "pct": round(100 * len(done) / len(execs)) if execs else 0},
        "milestones": [{"id": e.get("id"), "phase": e.get("phase"), "item": e.get("item"),
                        "done": bool(e.get("done")),
                        "metric": (e.get("eval") or {}).get("metric", ""),
                        "before": (e.get("eval") or {}).get("before", ""),
                        "after": (e.get("eval") or {}).get("after", "")} for e in execs],
        "low_hanging": [{"id": e.get("id"), "phase": e.get("phase"), "item": e.get("item")}
                        for e in execs if not e.get("done")][:3],
        "roadmap": [{"title": p.get("title"), "days": p.get("days"), "theme": p.get("theme"),
                     "milestone": p.get("milestone")} for p in (bundle.get("roadmap") or {}).get("phases", [])],
        "frontier": [{"name": f.get("name"), "recent_work": f.get("recent_work"),
                      "link": f.get("link"), "year": f.get("year"),
                      "summary": f.get("summary", "")} for f in (bundle.get("frontier") or [])],
        "collaborate": {
            "message": "Building in public — open an issue, PR an entry to data/*.yml, or reach out to co-analyze open aging data.",
            "hubs": [{"name": e.get("name"), "url": e.get("url"), "type": e.get("type"), "note": e.get("note")}
                     for e in eco if e.get("open_to_independents")],
        },
        "links": {
            "repo": repo, "dashboard": f"{SITE_BASE}/", "field_graph": f"{SITE_BASE}/graph.html",
            "updates_feed": f"{SITE_BASE}/feed.xml",
            "problems": f"{repo}/blob/main/docs/PROBLEMS.md",
            "gaps": f"{repo}/blob/main/docs/gaps-analysis.md",
            "fair": f"{repo}/blob/main/docs/FAIR.md", "nulls": f"{repo}/blob/main/docs/NULLS.md",
            "roadmap": f"{repo}/blob/main/docs/ROADMAP.md",
        },
    }


def main() -> int:
    bundle = {n: load(n) for n in ("meta", "loop", "roadmap", "turns", "frontier", "reflections",
                                   "executions", "people", "startups", "stack", "ecosystem")}
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(bundle, ensure_ascii=False, indent=2))
    tracker = build_tracker(bundle)
    TRACKER.write_text(json.dumps(tracker, ensure_ascii=False, indent=2))
    counts = {k: (len(v) if isinstance(v, list) else 1) for k, v in bundle.items()}
    print(f"Wrote {OUT.relative_to(ROOT)} — {counts}")
    print(f"Wrote {TRACKER.relative_to(ROOT)} — progress {tracker['progress']['pct']}% "
          f"({tracker['progress']['done']}/{tracker['progress']['total']}), "
          f"{len(tracker['milestones'])} milestones, {len(tracker['collaborate']['hubs'])} hubs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
