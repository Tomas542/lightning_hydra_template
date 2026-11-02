---
name: documentation-and-adrs
description: Records decisions and documentation for ML research codebases. Use when you need to document an architecture decision (ADR) or the reasoning behind a design choice, when changing model APIs, logging new dataset schemas, or recording context that future researchers and agents will need to understand the codebase.
---

# Documentation and ADRs (ML Research & Python Edition)

## Overview

Document decisions, not just code. The most valuable documentation in ML research captures the *why* — the architectural constraints, hardware limits, trade-offs, and experimental rationale that led to a specific model design or training pipeline. Code shows *what* was built; documentation explains *why it was structured this way* and *what alternative approaches were rejected*. This context is essential for future researchers, engineers, and AI agents.

## When to Use

- Making a significant architectural decision (e.g., switching from RNN to Transformer, adopting PyTorch Lightning or Hydra)
- Choosing between competing approaches (e.g., loss functions, tokenization strategies, audio feature extraction parameters)
- Adding or changing a shared API (`src/models/`, `src/data/`)
- Shipping a new model variant or dataset processing pipeline
- Onboarding new collaborators or AI agents to the project
- When you find yourself explaining the same training gotcha or preprocessing constraint repeatedly

**When NOT to use:** Don't document obvious code. Don't add comments that restate what the code already says. Don't write ADRs for throwaway experimental prototypes.

---

## Architecture Decision Records (ADRs)

ADRs capture the reasoning behind significant technical and modeling decisions. They are the highest-value documentation you can write in research.

### When to Write an ADR

- Choosing a foundational model architecture or pretrained checkpoint backbone
- Selecting loss functions, regularization techniques, or optimization algorithms
- Designing experiment configuration hierarchies (e.g., Hydra schema design)
- Choosing between data frameworks or audio/vision processing libraries (`librosa` vs `torchaudio`)
- Any architectural choice that would be expensive or time-consuming to reverse after a multi-day training run

### Match the existing convention first

Before creating an ADR, inspect the repository for established conventions (existing ADRs in `docs/adrs/` or `docs/decisions/`, project instructions, etc.). Match:
- **Location and format** — e.g., `docs/adrs/` or `docs/decisions/`.
- **Numbering and naming** — continue the existing sequence (`0001-use-hydra-config.md`, etc.).

### ADR Template

Store ADRs in `docs/adrs/` with sequential numbering:

```markdown
# ADR-001: Use Hydra for ML Experiment Configuration

## Status
Accepted

## Date
2026-10-24

## Context
We need a robust configuration management system for training machine learning models across multiple hardware environments. Key requirements:
- Hierarchical configuration composition (combining model, dataset, and optimizer configs)
- Command-line overrides for hyperparameter sweeps
- Reproducibility and easy logging of active configurations

## Decision
Use `hydra-core` for recursive YAML-based configuration management under `configs/`.

## Alternatives Considered

### Plain Python Dataclasses / Argparse
- Pros: No extra dependencies, full Python control
- Cons: Cumbersome command-line overrides for complex nested parameters, no built-in multi-run composition
- Rejected: Does not scale well as model complexity grows

### JSON / YAML configuration files loaded manually
- Pros: Simple parsing
- Cons: Lacks modular composition and dynamic overrides
- Rejected: Leads to code duplication across training scripts

## Consequences
- All training runs must define their entry point inside `configs/main.yaml`
- Parameters must be passed through configs rather than hardcoded in `src/`
- Team needs familiarity with Hydra composition syntax
```
## ADR Lifecycle

```markdown
PROPOSED → ACCEPTED → (SUPERSEDED or DEPRECATED)
```
Don't delete old ADRs. They capture historical research lineage.

## Inline Documentation

### When to Comment

1. Comment the why, not the what:

```py
# BAD: Restates the code
# Multiply tensor by scaling factor
x = x * 0.5

# GOOD: Explains non-obvious intent or tensor shape invariant
# Apply temperature scaling to logits before softmax to prevent overconfidence
# during early training epochs (see ADR-002 for temperature schedule rationale)
scaled_logits = logits / temperature
```

### When NOT to Comment

```py
# Don't comment self-explanatory code
def compute_accuracy(preds: Tensor, targets: Tensor) -> float:
    return (preds == targets).float().mean().item()

# Don't leave TODO comments for things you should just do now
# TODO: fix tensor shape bug  ← Just fix it

# Don't leave commented-out code
# old_model = CustomRNN()  ← Delete it, git history preserves it
```

### Document Known Gotchas in ML Pipelines

```py
"""IMPORTANT: Audio waveforms must be normalized to [-1.0, 1.0] before
passing into the MelSpectrogram transform, otherwise librosa feature extraction
will produce scaled outputs that trigger NaN losses in FP16 training.

See ADR-004 for audio pipeline specifications.
"""
def extract_features(waveform: np.ndarray) -> np.ndarray:
    ...
```

## Model & API Documentation (Python / PyTorch)

For model architectures, datasets, and public utility APIs in `src/`:

### Google-Style Docstrings (Preferred for Python / PyTorch)

```py
import torch
from torch import Tensor, nn

class AudioClassifier(nn.Module):
    """Audio classification model using convolutional frontends and attention.

    Attributes:
        config: Model configuration dataclass containing hyperparameters.
    """

    def __init__(self, config: ModelConfig) -> None:
        """Initializes the audio classifier.

        Args:
            config (ModelConfig): Configuration object containing model dimensions and dropout.

        Raises:
            ValueError: If hidden dimension is not divisible by attention heads.
        """
        super().__init__()
        self.config = config

    def forward(self, audio_inputs: Tensor) -> Tensor:
        """Computes forward pass and returns unnormalized class logits.

        Args:
            audio_inputs (Tensor): Tensor of shape (batch_size, sequence_length).

        Returns:
            Logits tensor of shape (batch_size, num_classes).
        """
        ...
```

## README structure

Every repository root should have a clear README:

# Project Name

One-paragraph description of the machine learning research repository.

## Quick Start

1. Clone the repo and install dependencies via Pixi:
```shell
pixi install
```

## Architecture

Brief overview of `src/` (source code), `configs/` (Hydra YAMLs), `test/` (pytest), and `docs/` (research notes and ADRs)

## Documentation for Agents

Special consideration for AI agent context:
- AGENTS.md — Global rules, tech stack (Python 3.12, torch==2.7.1, transformers==5.16.0, Hydra, Pixi), and file structure.
- Skills (`.agents/skills/`) — Modular operational playbooks loaded on demand.
- ADRs — Prevent agents from re-litigating past architectural or modeling decisions.
- Inline gotchas — Prevent agents from introducing tensor dimension mismatches or numerical instability.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The code is self-documenting" | Code shows tensor shapes and math, but not why a specific architecture or loss function was chosen over alternatives. |
| "We'll write docs when the model architecture stabilizes" | Architectures stabilize faster when documented. Writing the doc is the first test of the design. |
| "Nobody reads docs" | Architectures stabilize faster when documented. Writing the doc is the first test of the design. |
| "ADRs are overhead" | A 10-minute ADR prevents wasting GPU compute on hypotheses that were already rejected for architectural reasons. |

## Red Flags

- Significant architectural decisions or loss function choices with no written rationale
- Model modules and training functions with no type annotations or docstrings
- README that doesn't explain how to launch training or tests
- Commented-out model architectures instead of deletion
- No ADRs in a repository with complex custom architectures
- Documentation that restates code instead of explaining research intent

## Verification

After documenting:

[ ] ADRs exist in `docs/adrs/` for major architectural and modeling decisions
[ ] README covers quick start commands via Pixi and repository structure
[ ] Model and dataset functions in `src/` have Google-style docstrings and type hints
[ ] Known gotchas (audio sampling rates, tensor shape invariants) are documented inline
[ ] No commented-out model code remains
[ ] `AGENTS.md` is current and accurate
