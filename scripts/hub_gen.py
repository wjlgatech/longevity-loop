#!/usr/bin/env python3
"""hub_gen — validate + freshness-check the hub's JIT deep artifacts (docs/HUB_ARCHITECTURE.md).

Phase 2 of the hub: for a cited repo we generate a knowledge graph + a skill, SHA-stamped,
under hub/<repo>/ (grounded in the real repo — no evidence => no claim). This script is the
GATE and the FRESHNESS mechanism around those artifacts:

  hub_gen.py --check     # OFFLINE integrity gate (manifest well-formed, artifacts present,
                         # KG valid, SKILL.md has frontmatter) — wired into `make check`.
  hub_gen.py --refresh   # NETWORK: git ls-remote each repo HEAD vs the pinned source_sha,
                         # report FRESH/STALE (the "never ship stale" check; for the cron).
  hub_gen.py --selftest  # assert the validator catches a broken exemplar.

Deep generation itself (graphify / anyagent reverse) is done on demand; this keeps what's
committed honest and detects when it drifts from the source.
"""
from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
HUB = ROOT / "hub"
MANIFEST_KEYS = ("repo", "url", "source_sha", "artifacts")


def exemplars() -> list[pathlib.Path]:
    return sorted(p.parent for p in HUB.glob("*/manifest.json")) if HUB.exists() else []


def validate(d: pathlib.Path) -> list[str]:
    """Offline integrity checks for one hub/<repo>/ exemplar. Returns a list of problems."""
    errs = []
    try:
        man = json.loads((d / "manifest.json").read_text())
    except (OSError, json.JSONDecodeError) as e:
        return [f"{d.name}: unreadable manifest.json ({e})"]
    for k in MANIFEST_KEYS:
        if not man.get(k):
            errs.append(f"{d.name}: manifest missing '{k}'")
    if not re.fullmatch(r"[0-9a-f]{7,40}", str(man.get("source_sha", ""))):
        errs.append(f"{d.name}: source_sha not a commit hash ({man.get('source_sha')!r})")
    for art in man.get("artifacts", []):
        if not (d / art).exists():
            errs.append(f"{d.name}: artifact '{art}' listed but missing")
    kg = d / "knowledge-graph.json"
    if kg.exists():
        try:
            g = json.loads(kg.read_text())
            if not (isinstance(g.get("nodes"), list) and g["nodes"] and isinstance(g.get("edges"), list)):
                errs.append(f"{d.name}: knowledge-graph.json needs non-empty 'nodes' + 'edges'")
        except json.JSONDecodeError as e:
            errs.append(f"{d.name}: knowledge-graph.json invalid JSON ({e})")
    skill = d / "SKILL.md"
    if skill.exists():
        m = re.match(r"^---\n(.*?)\n---\n", skill.read_text(), re.S)
        if not m:
            errs.append(f"{d.name}: SKILL.md missing '---' frontmatter")
        elif not ("name:" in m.group(1) and "description:" in m.group(1)):
            errs.append(f"{d.name}: SKILL.md frontmatter needs name + description")
    return errs


def check() -> int:
    dirs = exemplars()
    if not dirs:
        print("hub: no exemplars yet (nothing to gate).")
        return 0
    problems = [e for d in dirs for e in validate(d)]
    if problems:
        print("HUB integrity FAILED:", file=sys.stderr)
        for p in problems:
            print(f"  ✗ {p}", file=sys.stderr)
        return 1
    print(f"hub integrity: OK — {len(dirs)} exemplar(s) "
          f"({', '.join(d.name for d in dirs)}) well-formed + SHA-stamped.")
    return 0


def refresh() -> int:
    """Network: is each exemplar still fresh vs the repo's live HEAD?"""
    rc = 0
    for d in exemplars():
        man = json.loads((d / "manifest.json").read_text())
        try:
            out = subprocess.run(["git", "ls-remote", man["url"], "HEAD"],
                                 capture_output=True, text=True, timeout=20, check=True).stdout
            live = out.split()[0][:len(str(man["source_sha"]))] if out else ""
        except Exception as e:  # noqa: BLE001
            print(f"  ? {d.name}: could not reach {man['url']} ({type(e).__name__})")
            continue
        fresh = live == man["source_sha"]
        print(f"  {'✅ FRESH' if fresh else '♻ STALE'} {d.name}: pinned {man['source_sha']} "
              f"{'==' if fresh else '!='} live {live} — {'up to date' if fresh else 'regenerate'}")
        rc = rc or (0 if fresh else 2)
    return rc


def selftest() -> int:
    # the real exemplar must validate clean
    for d in exemplars():
        assert not validate(d), f"exemplar {d.name} should be clean: {validate(d)}"
    # a synthetic broken manifest must be caught
    import tempfile
    with tempfile.TemporaryDirectory() as t:
        bad = pathlib.Path(t) / "broken"
        bad.mkdir()
        (bad / "manifest.json").write_text('{"repo": "x"}')  # missing keys + bad sha
        assert validate(bad), "validator must flag a broken manifest"
    print(f"hub_gen selftest: OK ({len(exemplars())} exemplar(s) clean; broken manifest caught).")
    return 0


def main() -> int:
    if "--refresh" in sys.argv:
        return refresh()
    if "--selftest" in sys.argv:
        return selftest()
    return check()  # default + --check


if __name__ == "__main__":
    raise SystemExit(main())
