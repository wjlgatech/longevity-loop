#!/usr/bin/env python3
"""Turn 01 — Systems-Age-motivated baseline.

Question (Levine 2025): does CROSS-CLOCK DISAGREEMENT add predictive signal over
the single best clock? We compute a panel of epigenetic clocks, then compare
outcome AUROC of [best single clock] vs [best single + across-clock std].

SCAFFOLD: the metric + comparison are real and runnable once you wire (a) the
Biolearn challenge data and (b) the clock panel (`# TODO(you)`). It computes a real
Δ across seeds and refuses to fabricate data or scores. Fill PROOF.md from the
output (report the null if the CIs overlap).

Docs: https://bio-learn.github.io/  ·  clocks: biolearn ModelGallery or pyaging.
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import train_test_split

OUT = pathlib.Path(__file__).parent / "results.json"
SEEDS = [0, 1, 2, 3, 4]


def load_challenge():
    """Return (meth_df, chrono_age: np.ndarray, outcome: np.ndarray[0/1]).

    TODO(you): wire the Biomarkers-of-Aging Challenge data via Biolearn, e.g.
        from biolearn.data_library import DataLibrary
        d = DataLibrary().get("<challenge_dataset_id>").load()
        return d.dnam, d.metadata["age"].values, (d.metadata["outcome"] == 1).astype(int).values
    We do NOT fabricate data.
    """
    raise NotImplementedError("Wire the Biolearn challenge dataset (see docstring).")


def clock_panel(meth_df, chrono_age) -> dict[str, np.ndarray]:
    """Return {clock_name: age_acceleration} for a panel of clocks.

    TODO(you): compute several clocks with Biolearn/pyaging and return
    (predicted_age - chronological_age) per clock, e.g.
        from biolearn.model_gallery import ModelGallery
        g = ModelGallery()
        return {n: g.get(n).predict(meth_df)["predicted"].values - chrono_age
                for n in ["Horvathv1", "PhenoAge", "GrimAgeV2", "DunedinPACE"]}
    """
    raise NotImplementedError("Compute a clock panel via Biolearn/pyaging (see docstring).")


def _auc(X: np.ndarray, y: np.ndarray, seed: int) -> float:
    xtr, xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=seed, stratify=y)
    clf = LogisticRegression(max_iter=1000).fit(xtr, ytr)
    return roc_auc_score(yte, clf.predict_proba(xte)[:, 1])


def main() -> int:
    meth, chrono, outcome = load_challenge()
    panel = clock_panel(meth, chrono)                    # {name: accel[n]}
    names = list(panel)
    A = np.column_stack([panel[n] for n in names])       # [n_samples, n_clocks]

    # best single clock (by its own solo AUROC on seed 0)
    solo = {n: _auc(A[:, [i]], outcome, 0) for i, n in enumerate(names)}
    best_i = int(np.argmax([solo[n] for n in names]))
    best = A[:, [best_i]]
    hetero = A.std(axis=1, keepdims=True)                # cross-clock disagreement
    combo = np.hstack([best, hetero])

    single_auc = np.array([_auc(best, outcome, s) for s in SEEDS])
    combo_auc = np.array([_auc(combo, outcome, s) for s in SEEDS])
    delta = combo_auc - single_auc
    result = {
        "anchor": "Levine, Systems Age (Nature Aging 2025)",
        "metric": "outcome AUROC (5 seeds)",
        "best_single_clock": names[best_i],
        "single": {"mean": float(single_auc.mean()), "std": float(single_auc.std())},
        "single_plus_heterogeneity": {"mean": float(combo_auc.mean()), "std": float(combo_auc.std())},
        "delta_mean": float(delta.mean()), "delta_std": float(delta.std()),
        "verdict": "heterogeneity helps" if delta.mean() - delta.std() > 0 else "no lift (null)",
    }
    OUT.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print("\nFill PROOF.md honestly (incl. a null), then @DrMorganLevine with the artifact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
