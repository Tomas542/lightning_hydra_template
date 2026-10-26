---
name: code-review
description: Conducts multi-axis code review for Python, PyTorch, and ML research codebases. Use before merging any change. Use when reviewing code written by yourself, another agent, or a human. Use when you need to assess code quality across multiple dimensions (correctness, readability, architecture, security, performance) before it enters the main branch. Use when asked to review a diff or a pull request.
---

# Code Review and Quality (ML Research & Python Edition)

## Overview

Multi-dimensional code review with strict quality gates for Machine Learning and Python projects. Every change gets reviewed before merge — no exceptions. Review covers five axes: correctness (including tensor/numerical verification), readability, architecture, security, and performance.

**The approval standard:** Approve a change when it definitely improves overall code health and research reproducibility, even if it isn't perfect. Don't block a change because it isn't exactly how you would have written it. If it improves the codebase and follows the project's conventions (`Python 3.12`, `torch==2.7.1`, `transformers==5.16.0`, `Hydra`, `Pixi`), approve it.

## When to Use

- Before merging any PR or change into `src/`, `configs/`, or `test/`
- After completing a feature implementation or new model architecture
- When another agent or model produced code you need to evaluate
- When refactoring existing dataset pipelines, training loops, or loss functions
- After any bug fix (review both the fix and the regression test in `test/`)

---

## The Five-Axis Review

Every review evaluates code across these dimensions:

### 1. Correctness & Numerical Integrity

Does the code do what it claims to do without breaking reproducibility or tensor computations?

- Does it match the research spec or issue requirements?
- Are edge cases handled (empty batches, single-sample batches, variable-length sequences/audio)?
- Are error paths handled (e.g., catching dataset corruption, missing keys in config)?
- **Is determinism preserved?** Are random seeds explicitly set (`torch.manual_seed`, `np.random.seed`) across standard library, NumPy, and PyTorch?
- Does it pass all tests (`pixi run -e test pytest`)? Are the tests actually testing tensor shapes, gradients, and loss computations?
- Are there hidden shape mismatches, broadcast errors, off-by-one index shifts, or `NaN`/`Inf` propagations in loss steps?

### 2. Readability & Simplicity

Can another researcher (or agent) understand this model or training loop without the author explaining it?

- Are names descriptive and consistent with Python/ML conventions? (Use `inputs`, `targets`, `logits`, `loss` instead of vague variables like `x`, `y`, `temp`, `data` without context).
- Are functions and modules typed with Python 3.12 syntax and Google-style docstrings?
- Is the control flow straightforward (avoiding deep nested conditionals inside custom loss layers or training loops)?
- **Could this be done in fewer lines?** (1000 lines in `train.py` where 100 suffice is a failure).
- **Are abstractions earning their complexity?** (Don't build complex custom trainer classes until PyTorch/Hydra default patterns are insufficient).
- Would comments clarify non-obvious math, tensor transformations, or dimension shuffling?
- Are there dead code artifacts: unused imports, commented-out loss functions, or old model variants left behind?

### 3. Architecture & ML Conventions

Does the change fit the system's design and modular repository setup?

- Does it follow project conventions (`src/` for source, `configs/` for Hydra YAML configs, `test/` for pytest)?
- Are hyperparameters passed via Hydra configuration files instead of being hardcoded in `src/`?
- Is feature extraction or dataset transformation logic decoupled from the model architecture?
- Are dependencies flowing in the right direction (e.g., models do not import from high-level training scripts)?
- **Does this refactor reduce complexity or just relocate it?** Deleting an unused model variant or simplifying a data pipeline is better than wrapping it in a complex factory object.
- **Is feature-specific logic leaking into shared modules?** (e.g., custom dataset normalization leaking into general-purpose model layers).
- **Are tensor type boundaries and shape invariants explicit?** Question untyped dictionaries (`dict[str, Any]`) passed between data loaders and models when structured dataclasses or explicit tensor shape hints could clarify intent.

### 4. Security & Safety

Does the change introduce security vulnerabilities or compromise model/data safety?

- Are local or downloaded model weights scanned before execution (`pixi run -e safe scan_model`)?
- Are virtual environments scanned when dependencies change (`pixi run -e safe scan_envs`)?
- Are secrets, API keys (WandB, Hugging Face tokens), or credentials kept out of code, logs, and version control?
- Are file paths sanitized when loading external dataset files or local checkpoints?
- Is data from external sources (user input, remote datasets, web artifacts) treated as untrusted?
- Are environment variables (e.g., `CUDA_VISIBLE_DEVICES`, `HTTP_PROXY`) kept out of tracked files like `README.md`?

### 5. Performance & Resource Efficiency

Does the change introduce hardware bottlenecks or memory inefficiencies?

- Are tensor operations efficiently batched (avoiding Python `for` loops over batch dimensions)?
- Are tensors moved to GPU devices efficiently (avoiding redundant host-to-device transfers)?
- Are gradients zeroed out properly (`optimizer.zero_grad(set_to_none=True)`) to optimize memory?
- Are PyTorch evaluation loops wrapped in `torch.no_grad()` or `torch.inference_mode()`?
- Are DataLoader worker parameters (`num_workers`, `pin_memory`) configured to prevent CPU bottlenecks?
- Are large intermediate tensors held in memory across training steps causing VRAM leaks?

---

## Structural Remedies

When you flag a structural problem, propose the move — not just the problem:

- **Replace a chain of nested `if/elif` blocks in loss/model selection** with an `Enum` or explicit registry/dispatcher.
- **Extract a long training step** into modular helper functions (`move_batch_to_device`, `compute_loss`, `clip_and_step`).
- **Separate dataset preprocessing from model forward pass** so each can be unit-tested independently.
- **Move hardcoded hyperparameters** out of Python source files into `configs/`.
- **Reuse standard PyTorch/Transformers utilities** instead of writing custom, untested tensor manipulation hacks.
- **Delete dead model variants or obsolete scripts** rather than leaving them commented out.

---

## Change Sizing

Small, focused changes are easier to review, faster to merge, and safer to deploy. Target these sizes:
```
~100 lines changed   → Good. Reviewable in one sitting.
~300 lines changed   → Acceptable if it's a single logical model or dataset update.
~1000 lines changed  → Too large. Split it.
```
**Watch file size, not just diff size.** Around 500–1000 total lines in a single file (e.g., a massive `dataset.py` or `model.py`) is an inspection signal. Extract sub-modules, helper functions, or layer definitions before adding new functionality.

**Separation Rule:** A change that refactors existing model code and introduces a new loss function or architecture should be submitted as separate PRs/commits.

---

## Review Process

### Step 1: Understand the Context

- What hypothesis or model improvement is this change addressing?
- What configuration files or dataset loaders are affected?
- What is the expected metric or performance impact?

### Step 2: Review the Tests First (`test/`)

- Do unit tests exist in `test/` for core functionality added to `src/`?
- Do tests verify tensor shapes, gradient flow, and loss values?
- Would tests catch a regression if tensor indices or shapes changed?
- *Mutation Test:* Mentally or temporarily swap an index, drop a mask, or change a sign in the forward pass and check if pytest fails. If tests stay green, flag the missing test case.

### Step 3: Review the Implementation

Walk through the code across the five axes:
1. **Correctness:** Does it compute metrics/tensors correctly? Is seeding preserved?
2. **Readability:** Are Python type hints and docstrings present? Is the flow simple?
3. **Architecture:** Does it conform to `src/`, `configs/`, and project patterns?
4. **Security:** Were model weight scans and env scans run if applicable?
5. **Performance:** Are VRAM, batching, and GPU operations optimized?

### Step 4: Categorize Findings

Label every review comment with a clear severity level:

| Prefix | Meaning | Action Required |
| :--- | :--- | :--- |
| *(no prefix)* | Required change | Must address before merging |
| **Critical:** | Blocks merge | Numerical bug, security issue, memory leak, unverified weight scan |
| **Nit:** | Minor, optional | Formatting preference, minor docstring adjustment |
| **Optional / Consider:** | Suggestion | Architectural idea, minor cleanup suggestion |
| **FYI:** | Informational | Context or reference note for future iterations |

### Step 5: Check Verification & Tooling

Check project compliance:
- Formatted via `pixi run -e dev format <file>`
- Checked/linted via `pixi run -e dev check_fix <file>`
- Smoke test or unit tests verified via `pixi run -e test pytest <file>`


## The Review Checklist

```markdown
## Review: [Change Title]

### Context & Functional Verification
- [ ] I understand what model, dataset, or utility change this introduces
- [ ] Smoke test / fast dev run verified on small dataset sample

### Correctness & Reproducibility
- [ ] Tensor shapes, backward passes, and loss calculations are mathematically correct
- [ ] Seeding and determinism are strictly preserved
- [ ] Edge cases (empty batches, sequence truncation, NaN values) are handled
- [ ] Unit tests added under `test/` for new core functionality in `src/`

### Readability & Python Quality
- [ ] Type annotations (Python 3.12) present for arguments and return values
- [ ] Google-style docstrings present for classes and non-init functions
- [ ] Code formatted with `pixi run -e dev format`
- [ ] No unneeded complexity or dead code

### Architecture & Repository Conventions
- [ ] Hyperparameters located in `configs/`, code located in `src/`
- [ ] Modular code structure maintained (e.g., `src/models/`, `src/data/`)
- [ ] No hardcoded paths, local environment variables, or proxies in tracking files

### Security & Safety
- [ ] No hardcoded API keys, tokens, or credentials
- [ ] Weight scanning executed for new model checkpoints (`scan_model`)
- [ ] Env scanning executed for dependency changes (`scan_envs`)

### Performance
- [ ] No unbatched Python loops over tensors
- [ ] Evaluation loops use `torch.no_grad()` / `torch.inference_mode()`
- [ ] VRAM memory allocation clean without leaks

### Verdict
- [ ] **Approve** — Ready to merge
- [ ] **Request Changes** — Required issues must be addressed
```

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The loss is decreasing, so the math must be right" | Loss can decrease even with incorrect masking, data leakage, or subtle index bugs. Tests are mandatory. |
| "I'll clean up the dataset script after training finishes" | Messy data pipelines cause silent bugs that invalidate long training runs. Clean before launching. |
| "It's just a small hyperparameter tweak, no need for Hydra" | Hardcoded hyperparameters ruin reproducibility across experiment runs. Move them to `configs/`. |
| "The PyTorch model works without type hints" | Type hints prevent silent shape mismatches and make automated refactoring reliable. |

## Red Flags to Block

- Hardcoding CUDA_VISIBLE_DEVICES or proxy settings in repository files.
- Adding broad try/except blocks that swallow model runtime or CUDA errors.
- Committing model weights directly to Git.
- Modifying evaluation metrics or test suites without explicit instructions.
