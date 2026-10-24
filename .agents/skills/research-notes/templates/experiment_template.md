# Experiment Run Log Template

**Experiment Name:** [Insert Unique Name]
**Date:** YYYY-MM-DD
**Git Commit Hash:** [Insert Hash]

---

## 1. Experimental Objective
- **Hypothesis:** What specific architectural change, loss modification, or hyperparameter shift is being tested?
- **Expected Outcome:** What metric delta or convergence behavior is predicted?

---

## 2. Configuration & Overrides
- **Hyra log dir:** `logs/runs/{date}/{exp_name}`
- **Modified Overrides:**
  - `model.architecture = ...`
  - `optimizer.lr = ...`

---

## 3. Quantitative Results
| Evaluation Metric | Baseline Value | Current Experiment Value | Delta (%) |
| :--- | :--- | :--- | :--- |
| **Validation Loss** | 0.000 | 0.000 | 0.00% |
| **Target Accuracy / Metric** | 0.0 | 0.0 | +0.0% |

---

## 4. Observations & Failure Analysis
- **Training Stability:** [e.g., Smooth convergence, gradient spikes around step 500]
- **Resource Utilization:** [e.g., VRAM usage, peak throughput]
- **Next Steps:** [Actionable items derived from this run]
