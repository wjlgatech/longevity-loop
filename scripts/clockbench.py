#!/usr/bin/env python3
"""clockbench — a standardized, reproducible CROSS-CLOCK DISAGREEMENT benchmark.

The #1 gap this repo's research triangulated across all three time windows
(30 days / 30 years / 300 years, see docs/gaps-analysis.md) is *measurement*:
"the epigenetic clocks contradict each other and no consensus clock has won,"
with "no shared held-out benchmark." You can't optimize what you can't measure.

This turns that complaint into a NUMBER anyone can compute the same way on the
same data. Given a matrix of biological-age estimates (rows = samples/people,
cols = clocks), it reports:
  • pairwise clock AGREEMENT (Spearman rank correlation) — do clocks even rank people the same?
  • per-CLOCK consensus score + the systematic OUTLIER clock (lowest mean agreement)
  • per-SAMPLE dispersion (spread of estimates for one person; CV, range) — for whom do clocks disagree most?
  • one headline number: mean pairwise agreement across the whole panel.

Dependency-free (stdlib `statistics` only — the metric is simple math, no reason
to pull numpy/scipy). Runs today on a deterministic synthetic panel; wire real
`pyaging`/Biolearn clock outputs via --input (same honest-scaffold pattern as
turns/*/baseline.py — real metric, you supply the data).

  clockbench.py --demo                 # deterministic synthetic panel → report
  clockbench.py --input clocks.csv     # real data: header=clock names, rows=samples
  clockbench.py --selftest             # assert the metrics behave (CI-safe, no data)
"""
from __future__ import annotations

import argparse
import json
import pathlib
import statistics as st

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT_MD = ROOT / "data" / "_clockbench.md"      # GENERATED review artifact (like _synthesis.md)
OUT_JSON = ROOT / "data" / "_clockbench.json"


def spearman(x: list[float], y: list[float]) -> float:
    """Spearman rank correlation via stdlib (Python 3.12+: correlation(method='ranked'))."""
    return st.correlation(x, y, method="ranked")


def read_csv(path: pathlib.Path) -> tuple[list[str], list[list[float]]]:
    """CSV → (clock_names, samples). Header = clock names; an optional leading
    non-numeric column (sample id) is dropped. Rows with a non-parseable cell are skipped."""
    lines = [ln for ln in path.read_text().splitlines() if ln.strip()]
    header = [h.strip() for h in lines[0].split(",")]
    id_col = 0
    # detect a leading id column: its first data cell isn't a float
    if len(lines) > 1:
        first = lines[1].split(",")[0].strip()
        try:
            float(first)
        except ValueError:
            id_col = 1
    clocks = header[id_col:]
    rows: list[list[float]] = []
    for ln in lines[1:]:
        cells = ln.split(",")[id_col:]
        try:
            rows.append([float(c) for c in cells])
        except ValueError:
            continue
    return clocks, rows


def demo_panel() -> tuple[list[str], list[list[float]]]:
    """Deterministic synthetic panel (NO randomness → byte-reproducible). Four clocks
    over 40 'people': three broadly agree with a latent true age; one is a systematic
    outlier that ranks people differently. Labeled synthetic — not a scientific result."""
    clocks = ["ClockA", "ClockB", "ClockC", "OutlierClock"]
    rows = []
    for i in range(40):
        true_age = 30 + i  # 30..69
        wobble = ((i * 7) % 11) - 5          # deterministic small bias, in [-5, 5]
        rows.append([
            true_age + wobble * 0.3,          # A: tight
            true_age + wobble * 0.6 + 1.0,    # B: looser, small offset
            true_age - wobble * 0.4,          # C: tight, opposite small bias
            60 + ((i * 13) % 20) - true_age * 0.15,  # Outlier: weakly/─vely related to age
        ])
    return clocks, rows


def analyze(clocks: list[str], rows: list[list[float]]) -> dict:
    n_clocks = len(clocks)
    cols = [[row[c] for row in rows] for c in range(n_clocks)]

    # pairwise agreement matrix (Spearman)
    pair = {}
    for a in range(n_clocks):
        for b in range(a + 1, n_clocks):
            r = round(spearman(cols[a], cols[b]), 4)
            pair[f"{clocks[a]}~{clocks[b]}"] = r
    headline = round(st.mean(pair.values()), 4) if pair else float("nan")

    # per-clock consensus = mean agreement with the other clocks
    per_clock = {}
    for a in range(n_clocks):
        others = [spearman(cols[a], cols[b]) for b in range(n_clocks) if b != a]
        per_clock[clocks[a]] = round(st.mean(others), 4) if others else float("nan")
    outlier = min(per_clock, key=per_clock.get) if per_clock else None

    # per-sample dispersion: spread of a single person's estimates across clocks
    disp = []
    for i, row in enumerate(rows):
        m = st.mean(row)
        sd = st.pstdev(row)
        disp.append({"sample": i, "mean": round(m, 2), "stdev": round(sd, 2),
                     "cv": round(sd / m, 4) if m else float("nan"),
                     "range": round(max(row) - min(row), 2)})
    median_cv = round(st.median(d["cv"] for d in disp), 4) if disp else float("nan")
    worst = sorted(disp, key=lambda d: d["range"], reverse=True)[:5]

    return {"n_samples": len(rows), "n_clocks": n_clocks, "clocks": clocks,
            "headline_mean_agreement": headline, "pairwise": pair,
            "per_clock_consensus": per_clock, "outlier_clock": outlier,
            "median_sample_cv": median_cv, "worst_dispersion": worst}


def write_report(res: dict, source: str) -> None:
    OUT_JSON.write_text(json.dumps(res, indent=2))
    L = [
        "# clockbench — cross-clock disagreement report (GENERATED)",
        "",
        f"> Source: **{source}**. Reproducible: `python3 scripts/clockbench.py` on the same input",
        "> yields identical numbers. This measures how much a panel of biological-age clocks",
        "> AGREES — the measurable core of gaps-analysis.md G1. No claim beyond the numbers.",
        "",
        f"- Samples: **{res['n_samples']}** · Clocks: **{res['n_clocks']}**",
        f"- **Headline — mean pairwise agreement (Spearman): {res['headline_mean_agreement']}** "
        "(1.0 = clocks rank people identically; ~0 = no agreement)",
        f"- Systematic outlier clock: **{res['outlier_clock']}** (lowest mean agreement)",
        f"- Median per-person dispersion (CV across clocks): **{res['median_sample_cv']}**",
        "",
        "## Per-clock consensus (mean agreement with the rest)",
    ]
    for c, v in sorted(res["per_clock_consensus"].items(), key=lambda kv: -kv[1]):
        L.append(f"- {c}: {v}" + ("  ⚠ outlier" if c == res["outlier_clock"] else ""))
    L += ["", "## Pairwise agreement"]
    L += [f"- {k}: {v}" for k, v in res["pairwise"].items()]
    L += ["", "## People the clocks disagree on most (top 5 by range of estimates)"]
    L += [f"- sample {d['sample']}: range {d['range']} yr (mean {d['mean']}, CV {d['cv']})"
          for d in res["worst_dispersion"]]
    L.append("")
    OUT_MD.write_text("\n".join(L))


def selftest() -> int:
    """Assert the metrics behave — CI-safe, no external data."""
    assert round(spearman([1, 2, 3, 4], [1, 2, 3, 4]), 6) == 1.0, "identical → +1"
    assert round(spearman([1, 2, 3, 4], [4, 3, 2, 1]), 6) == -1.0, "reversed → -1"
    clocks, rows = demo_panel()
    res = analyze(clocks, rows)
    assert res["n_samples"] == 40 and res["n_clocks"] == 4
    assert res["outlier_clock"] == "OutlierClock", f"expected OutlierClock, got {res['outlier_clock']}"
    # the three real clocks must agree with each other more than with the outlier
    good = [res["per_clock_consensus"][c] for c in ("ClockA", "ClockB", "ClockC")]
    assert min(good) > res["per_clock_consensus"]["OutlierClock"], "good clocks must out-agree outlier"
    assert -1.0 <= res["headline_mean_agreement"] <= 1.0
    print("clockbench selftest: OK (spearman bounds, outlier detection, demo analysis).")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Cross-clock disagreement benchmark.")
    ap.add_argument("--input", type=pathlib.Path, help="CSV: header=clock names, rows=samples")
    ap.add_argument("--demo", action="store_true", help="run on the deterministic synthetic panel")
    ap.add_argument("--selftest", action="store_true", help="assert metrics behave (no data)")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if args.input:
        clocks, rows = read_csv(args.input)
        source = f"{args.input} ({len(rows)} samples)"
    else:  # default to demo so the harness is always runnable
        clocks, rows = demo_panel()
        source = "SYNTHETIC demo panel (deterministic; not a scientific result)"
    if len(rows) < 2 or len(clocks) < 2:
        print("Need ≥2 samples and ≥2 clocks.", flush=True)
        return 1
    res = analyze(clocks, rows)
    write_report(res, source)
    print(f"clockbench: {res['n_clocks']} clocks × {res['n_samples']} samples · "
          f"mean agreement {res['headline_mean_agreement']} · outlier {res['outlier_clock']}")
    print(f"  wrote {OUT_MD.relative_to(ROOT)} + {OUT_JSON.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
