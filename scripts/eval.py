#!/usr/bin/env python3
"""Execution eval — the roadmap's checkbox + before→after report, kept honest.

Rule (gated in `make check`): an execution marked `done: true` MUST carry a real
`eval.before` AND `eval.after` (neither empty nor "pending"). No evidence ⇒ it is
NOT done. Prints the scoreboard + progress; `--gate` exits non-zero on a violation.
"""
from __future__ import annotations

import argparse
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
EXECS = yaml.safe_load((ROOT / "data" / "executions.yml").read_text()) or []
_PENDING = {"", "pending", "tbd", "n/a (pending)", None}


def violations() -> list[str]:
    out = []
    for e in EXECS:
        ev = e.get("eval") or {}
        if e.get("done"):
            for k in ("before", "after"):
                if str(ev.get(k, "")).strip().lower() in _PENDING:
                    out.append(f"{e['id']}: marked done but eval.{k} is pending/empty (no evidence ⇒ not done)")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", action="store_true")
    ap.parse_args()
    done = [e for e in EXECS if e.get("done")]
    pct = round(100 * len(done) / len(EXECS)) if EXECS else 0
    print(f"Roadmap execution: {len(done)}/{len(EXECS)} done ({pct}%)\n")
    for e in EXECS:
        box = "✅" if e.get("done") else "⬜"
        ev = e.get("eval") or {}
        print(f"  {box} {e['id']} {e['item']}")
        print(f"       {ev.get('metric','?')}: {ev.get('before','?')}  →  {ev.get('after','?')}")
    v = violations()
    if v:
        print("\nEVAL VIOLATIONS (a done item without a real before→after = a fake ✅):", file=sys.stderr)
        for x in v:
            print(f"  ✗ {x}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
