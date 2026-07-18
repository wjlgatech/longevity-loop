# clockbench — cross-clock disagreement report (GENERATED)

> Source: **SYNTHETIC demo panel (deterministic; not a scientific result)**. Reproducible: `python3 scripts/clockbench.py` on the same input
> yields identical numbers. This measures how much a panel of biological-age clocks
> AGREES — the measurable core of gaps-analysis.md G1. No claim beyond the numbers.

- Samples: **40** · Clocks: **4**
- **Headline — mean pairwise agreement (Spearman): 0.3151** (1.0 = clocks rank people identically; ~0 = no agreement)
- Systematic outlier clock: **OutlierClock** (lowest mean agreement)
- Median per-person dispersion (CV across clocks): **0.1077**

## Per-clock consensus (mean agreement with the rest)
- ClockA: 0.542
- ClockB: 0.5402
- ClockC: 0.528
- OutlierClock: -0.3498  ⚠ outlier

## Pairwise agreement
- ClockA~ClockB: 0.9989
- ClockA~ClockC: 0.975
- ClockA~OutlierClock: -0.348
- ClockB~ClockC: 0.966
- ClockB~OutlierClock: -0.3443
- ClockC~OutlierClock: -0.357

## People the clocks disagree on most (top 5 by range of estimates)
- sample 3: range 43.05 yr (mean 44.14, CV 0.3942)
- sample 6: range 38.2 yr (mean 45.9, CV 0.3381)
- sample 1: range 38.15 yr (mean 40.84, CV 0.3898)
- sample 9: range 33.35 yr (mean 47.66, CV 0.2861)
- sample 4: range 33.3 yr (mean 42.6, CV 0.3298)
