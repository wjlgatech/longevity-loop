#!/usr/bin/env python3
"""fair — score the open aging datasets against the FAIR principles → docs/FAIR.md.

Bridges gaps-analysis.md G2 (data integrity & reproducibility: "no FAIR data + metadata
standards for multi-omic aging data"). FAIR = Findable · Accessible · Interoperable ·
Reusable. This reads the datasheet in data/datasets.yml, scores each dataset
deterministically, and generates a public scorecard so a researcher can see at a glance
which open aging datasets are actually reproducible-friendly — and so this loop only builds
on FAIR-enough data.

Honesty (same discipline as the rest of the repo): each FAIR dimension is yes|partial|no;
an unknown/missing dimension counts as **no**, never a fake pass, and `--gate` fails the
build if any dataset has an unassessed dimension ("no unmeasured passes").

  fair.py            # write docs/FAIR.md
  fair.py --check    # compare instead of writing (drift gate, like build.py --check)
  fair.py --gate     # fail if any dataset has an unassessed FAIR dimension
  fair.py --selftest # assert the scoring behaves (CI-safe, no network)
"""
from __future__ import annotations

import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "datasets.yml"
OUT = ROOT / "docs" / "FAIR.md"
LEVELS = {"yes": 1.0, "partial": 0.5, "no": 0.0}
DIMS = ("findable", "accessible", "interoperable", "reusable")
MARK = {"yes": "🟢", "partial": "🟡", "no": "🔴"}


def esc(t: object) -> str:
    return " ".join(str("" if t is None else t).split())


def load() -> list[dict]:
    return (yaml.safe_load(DATA.read_text()) if DATA.exists() else []) or []


def score(ds: dict) -> tuple[int, dict, list[str]]:
    """Return (0-100 FAIR score, {dim: level}, unassessed dims)."""
    fair = ds.get("fair") or {}
    dims, unassessed = {}, []
    for d in DIMS:
        raw = fair.get(d)
        # YAML 1.1 turns unquoted yes/no into booleans — normalize so both forms work.
        lvl = "yes" if raw is True else "no" if raw is False else str(raw).lower() if raw is not None else ""
        if lvl not in LEVELS:
            unassessed.append(d)
            lvl = "no"  # no evidence ⇒ No (never a fake pass)
        dims[d] = lvl
    pct = round(100 * sum(LEVELS[v] for v in dims.values()) / len(DIMS))
    return pct, dims, unassessed


def render() -> str:
    rows = load()
    scored = sorted(((ds, *score(ds)) for ds in rows), key=lambda t: -t[1])
    repo = round(sum(s for _, s, _, _ in scored) / len(scored)) if scored else 0
    L = [
        "# longevity-loop — FAIR dataset scorecard", "",
        "_Generated from `data/datasets.yml` by `scripts/fair.py` — do not edit by hand._", "",
        "How **FAIR** (Findable · Accessible · Interoperable · Reusable) are the open aging "
        "datasets this loop uses? The field lacks shared FAIR/metadata standards for multi-omic "
        "aging data (gaps-analysis.md G2), so each dataset is scored on a transparent rubric and "
        "the loop prefers to build on the FAIR-est open data.", "",
        f"**Panel FAIR score: {repo}/100** across {len(scored)} datasets. "
        "🟢 yes = 1 · 🟡 partial = 0.5 · 🔴 no = 0. Unknown ⇒ no (never a fake pass).", "",
        "| Dataset | Access | F | A | I | R | FAIR | How to load |",
        "|---|:--|:-:|:-:|:-:|:-:|--:|---|",
    ]
    for ds, pct, dims, _ in scored:
        cells = " | ".join(MARK[dims[d]] for d in DIMS)
        L.append(f"| [{esc(ds['name'])}]({ds['url']}) | {esc(ds.get('access',''))} | {cells} | "
                 f"{pct} | `{esc(ds.get('load','—'))}` |")
    L += ["",
          "## Per-dataset provenance", ""]
    for ds, pct, _, _ in scored:
        L += [f"### {esc(ds['name'])} — FAIR {pct}/100",
              f"- **Access:** {esc(ds.get('access',''))} · **License:** {esc(ds.get('license','—'))}",
              f"- **Format:** {esc(ds.get('format','—'))} · **Persistent id:** {esc(ds.get('persistent_id','—'))}",
              f"- **Load:** `{esc(ds.get('load','—'))}`",
              f"- **Note:** {esc(ds.get('note',''))}", ""]
    L += ["---", "",
          "PR a dataset to `data/datasets.yml` with an honest FAIR self-assessment (unknown ⇒ `no`). "
          "Rubric: Findable (persistent id), Accessible (open, no gate), Interoperable (standard "
          "format), Reusable (clear license + load recipe).", ""]
    return "\n".join(L)


def selftest() -> int:
    assert score({"fair": {"findable": "yes", "accessible": "yes",
                           "interoperable": "yes", "reusable": "yes"}})[0] == 100, "all-yes → 100"
    assert score({"fair": {"findable": "no", "accessible": "no",
                           "interoperable": "no", "reusable": "no"}})[0] == 0, "all-no → 0"
    s, dims, un = score({"fair": {"findable": "yes"}})  # 3 missing
    assert s == 25 and set(un) == {"accessible", "interoperable", "reusable"}, "missing ⇒ no + flagged"
    assert score({"fair": {"findable": "partial", "accessible": "partial",
                           "interoperable": "partial", "reusable": "partial"}})[0] == 50
    print("fair selftest: OK (scoring bounds, unknown⇒no, completeness flagging).")
    return 0


def gate() -> int:
    bad = [(ds.get("name", "?"), un) for ds in load() if (un := score(ds)[2])]
    if bad:
        print("FAIR gate FAILED — unassessed dimensions (no unmeasured passes):", file=sys.stderr)
        for name, un in bad:
            print(f"  ✗ {name}: {', '.join(un)}", file=sys.stderr)
        return 1
    print(f"FAIR gate: OK — all {len(load())} datasets fully assessed.")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()
    if "--gate" in sys.argv:
        return gate()
    text = render()
    if "--check" in sys.argv:
        current = OUT.read_text() if OUT.exists() else ""
        if current != text:
            print("Out of date: docs/FAIR.md. Run `make fair`.", file=sys.stderr)
            return 1
        print("docs/FAIR.md is up to date.")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text)
    print(f"Wrote {OUT.relative_to(ROOT)} — {len(load())} datasets scored.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
