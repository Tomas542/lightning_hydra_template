---
name: eda
description: Runs structured Exploratory Data Analysis (EDA) on ML datasets before training. Computes length and parameter distributions (with boxplots and tail quantiles), compares train/val/test splits for shift and leakage, and logs reproducible findings to docs/notes/.
---

# Exploratory Data Analysis (EDA)

## Overview

Systematically inspect dataset structure, length/size distributions, class/label balance, and `train` / `val` / `test` split consistency before launching training runs. Catching skewed lengths, split distribution shift, or data leakage early prevents wasted compute and invalid benchmark claims.

## When to Use

- Onboarding a new dataset or custom split before building data loaders (`src/data/`).
- Auditing sequence lengths, audio durations, token counts, image resolutions, or tabular feature ranges.
- Comparing `train`, `val`, and `test` subsets for covariate shift, label imbalance, or group/ID overlap.
- Generating a reproducible dataset summary for `docs/notes/` or a paper's data section.

---

## Execution Workflow

### Step 1: Define Split & Metric Scope
Identify the dataset splits (`train`, `val`, `test`), primary sample identifier, grouping key (e.g., speaker ID, document ID, user ID, recording session), target/label column, and length/size attributes to inspect:
- **Length / Scale Metrics:** Duration in seconds, sample count, token count, character length, sequence frames, or bounding-box/feature counts.
- **Metadata / Context Metrics:** Sample rate, codec/format, language/domain tag, or missingness rate.

### Step 2: Analyze Length & Parameter Distributions
Compute summary statistics and visual distributions across the dataset and per split:
- **Central Tendency & Spread:** Count, mean, standard deviation, min, median (`p50`), `p90`, `p95`, `p99`, and max.
- **Boxplots & Tail Plots:** Generate boxplots (and complementary histograms/ECDFs on linear and log scales where skewed) comparing length/parameter distributions across splits or classes.
- **Truncation & Padding Risk:** Flag extreme outliers, zero-length/corrupt entries, and window/max-length truncation thresholds (e.g., percentage of samples clipped or heavily padded).

### Step 3: Compare `train`, `val`, and `test` Subsets
Audit split parity and potential leakage:
- **Label & Domain Proportions:** Compare class/category frequencies and domain/source ratios across `train`, `val`, and `test`.
- **Distribution Shift Checks:** Compare numeric/length distributions across splits using summary tables, boxplots, and two-sample statistical tests (e.g., Kolmogorov-Smirnov or Mann-Whitney U via `scipy.stats`, noting sample-size sensitivity).
- **Split Leakage & Group Overlap:** Check for exact duplicate IDs/hashes and verify whether grouping keys (such as speaker, source file, or session) leak across `train`, `val`, and `test`.

### Step 4: Write Reproducible Script & Log Findings
1. Keep EDA logic in a clean notebook under `notebook/` (using `pandas`, `numpy`, `scipy.stats`, and `matplotlib`/`seaborn` within the `pixi` environment) rather than mutating raw data.
2. Save generated plots (such as split length boxplots) to a deterministic output folder and record tables, observations, and action items in `docs/notes/eda-<dataset>.md` (aligned with `docs/ethics/reforms-framework.md` if present).

---

## Verification Checklist

- [ ] Length/parameter stats (`min`, `p50`, `p95`, `p99`, `max`) and boxplots are generated per split (`train`, `val`, `test`).
- [ ] Class/label balance and domain/metadata proportions are compared across all splits.
- [ ] Exact duplicates and grouping-key overlaps across splits are checked and reported.
- [ ] Actionable findings (e.g., max-length/chunking choices, stratification or split fixes) are documented in `docs/notes/`.
