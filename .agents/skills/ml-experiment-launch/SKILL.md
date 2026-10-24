---
name: ml-experiment-launch
description: Use when setting up, configuring, dry-running, or launching machine learning training and evaluation runs with Hydra and Pixi.
---

# ML Experiment Launch Guidelines

This skill defines the workflow for creating, configuring, and verifying machine learning experiments before full execution.

## 1. Hydra Configuration Rules
- All experiment configurations must live under `configs/` and be modularized (e.g., `configs/model/`, `configs/data/`, `configs/trainer/`).
- Main experiment entry point configuration must be named/updated inside `configs/main.yaml`.
- Do **not** hardcode hyperparameters (learning rates, batch sizes, seeds) inside `src/`. Pass all hyperparameter variables through Hydra configs.

## 2. Determinism & Seeding
Every launch script must explicitly enforce reproducibility. Set random seeds at the start of the execution script:
```python
import lightning.pytorch as L

def main(cfg):
    L.seed_everything(cfg.seed)
```

## 3. Pre-Launch Verification (Mandatory Workflow)
Before asking to run a full training job, execute the following plan-validate-execute loop:

### Weight & Environment Safety Scan:

If new local weights were downloaded:

```bash
pixi run -e safe scan_model /path/to/model
```

If dependencies were touched:

```bash
pixi run -e safe scan_envs
```

### Lint and Format check:

```bash
pixi run -e dev format <path_to_modified_files>
pixi run -e dev check_fix <path_to_modified_files>
```

### Execute Smoke Test:
Run a short sanity check on a tiny slice of data or 1–2 epochs/steps to verify loss computation, gradient backpropagation, and memory allocation:

```bash
pixi run python src/train.py trainer.fast_dev_run=True
```
## Launch Confirmation

Do not initiate full multi-epoch training or full dataset evaluation automatically. After a successful smoke test, present the following summary to the user and await explicit confirmation:

Config name and output directory.

Smoke test metrics (e.g., initial batch loss).

Total expected run duration / step count.
