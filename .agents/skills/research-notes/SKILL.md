---
name: research-notes
description: Use when logging experiment results, documenting hypotheses, creating research entries, or summarizing quantitative benchmark metrics.
---

# Research Notes & Experiment Logging

This skill standardizes how experimental results, hypotheses, and analytical findings are recorded to ensure full research lineage and reproducibility across agent sessions.

## 1. Storage Directory
- Save all research notes in `docs/notes/` (create if absent).
- File naming convention: `YYYY-MM-DD_<experiment_name>.md` (e.g., `2026-10-24_loss_ablation.md`).

## 2. Note Structure Template

When writing or updating a research note, follow this structure:

```markdown
# Experiment Note: [Short Descriptive Title]

**Date:** YYYY-MM-DD  
**Log dir:** `logs/runs/{date}/{exp_name}`
**Git Commit / Hash:** [Insert commit hash or status]  

## 1. Objective & Hypothesis
- **Goal:** Clear description of what is being tested.
- **Hypothesis:** Expected outcome and theoretical motivation.

## 2. System & Config Changes
- Key hyperparameter modifications (e.g., learning rate, weight decay, architecture changes) and their config changes and overrides.
- Code diff summary or relevant modules modified in `src/`.

## 3. Quantitative Results
Include key metrics evaluated during or after the run (loss, accuracy, F1, latency, throughput). Use markdown tables for clarity:

| Metric | Baseline | Experiment | Delta |
| :--- | :--- | :--- | :--- |
| Val Loss | 0.421 | 0.389 | -0.032 |
| Acc (%) | 88.4 | 90.1 | +1.7 |

## 4. Observations & Failure Analysis
- Qualitative insights (e.g., training stability, convergence speed, memory spikes).
- Unexpected behavior or edge-case failures.

## 5. Next Steps
- Actionable follow-ups based on these findings.
```

## 3. Metric Extraction Guidelines

- Extract values directly from output logs, tackio, or evaluation JSON outputs.
- Never estimate or fabricate metrics if a run timed out or failed; explicitly note interrupted runs as Incomplete/Failed.
- Always compare metrics against a specified baseline run.

## 4. Text style
Do not use common LLM generated text patterns, like—, excessive boldface, citation style quirks, emoji.
