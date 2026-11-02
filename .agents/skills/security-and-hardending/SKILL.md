---
name: security-and-hardening
description: Hardens code against vulnerabilities in Python, PyTorch, and ML research codebases. Use when auditing data loaders, model checkpoints, weight downloading scripts, configuration parsers, API integrations, or handling untrusted training data. Use when assessing supply-chain risks, malicious model weight deserialization, or verifying compliance.
---

# Security and Hardening (ML Research & Python Edition)

## Overview

Security-first development practices for Machine Learning research repositories. Treat every external dataset, every downloaded model weight (`.pt`, `.bin`, `.safetensors`), every remote API integration, and every dependency package as a potential vector. In ML, security spans code logic, model weight integrity, supply-chain verification, and data privacy.

## When to Use

- Downloading pretrained model weights or checkpoints from Hugging Face or external sources
- Building custom dataset loaders that ingest external CSVs, JSONs, audio, or image files
- Managing API keys and tokens (WandB, Hugging Face, Kaggle, GitHub)
- Integrating external services or webhooks in a research pipeline
- Auditing dependencies, lockfiles (`pixi.lock`, `pyproject.toml`), or build scripts
- Handling personal data, user annotations, or privacy compliance (GDPR/CCPA) in speech/vision datasets

---

## Process: Threat Model First for ML

Controls bolted on without a threat model are guesses. Before hardening an ML pipeline, consider these threat vectors:

1. **Map the trust boundaries.** Where does untrusted data cross into your system? Hugging Face model downloads, raw dataset directories, webhooks, Hugging Face Hub APIs, and untrusted command-line arguments. **Model weights (`torch.load`) are executable code** due to Python pickle deserialization.
2. **Name the assets.** Credentials (WandB/HF API tokens), proprietary datasets, model intellectual property, and compute cluster access.
3. **Run STRIDE over each boundary:**
   - **Spoofing:** Can someone impersonate a dataset source or registry?
   - **Tampering:** Can model weights or datasets be injected with poisoned samples or backdoors?
   - **Information disclosure:** Are API tokens or private dataset samples leaked into public logs or git commits?
   - **Denial of service:** Can malicious inputs cause infinite loops or GPU OOM crashes in data loaders?
   - **Elevation of privilege:** Can compromised script execution break out of container boundaries?

---

## The Three-Tier Boundary System

### Always Do (No Exceptions)

- **Scan model weights** before loading them locally (`pixi run -e safe scan_model <path>`).
- **Scan virtual environments and dependencies** after adding packages (`pixi run -e safe scan_envs`).
- **Parameterize and validate all inputs** at data ingestion boundaries (validate dataset column schemas, audio sample rates, shape dimensions).
- **Keep secrets out of version control** (never commit `.env`, API tokens, or SSH keys).
- **Use secure environment variables** for all credentials.

### Ask First (Requires Human Approval)

- Adding new external service integrations or APIs
- Downloading model checkpoints from unverified or non-canonical sources
- Modifying security scanner configurations or dependency rules
- Granting external access or publishing datasets containing PII/human annotations

### Never Do

- **Never load untrusted `.pt` or `.bin` files via `torch.load()` without scanning** (use `weights_only=True` or `safetensors` when possible).
- **Never commit API tokens, secrets, or `.env` files.**
- **Never log sensitive data** (passwords, tokens, personal identifiers in human speech/text datasets).
- **Never expose internal stack traces or cluster paths** in user-facing error messages.
- **Never use npm or other package manager for other languages** since you are working with Python package.

---

## Hardening Controls for ML

### 1. Model Weight Deserialization & Supply Chain (Pickle Vulnerabilities)
- Standard PyTorch `.pt` or `.bin` files rely on Python's `pickle` module, which can execute arbitrary code upon deserialization.
- **Mitigation:** Use `safetensors` format whenever possible (`transformers` supports `use_safetensors=True`). If loading `.pt` files, verify checksums and use `torch.load(..., weights_only=True)` to restrict unsafe global lookups.
- Run local model weight scans: `pixi run -e safe scan_model /path/to/model`.

### 2. Dataset Ingestion & Boundary Validation
- Untrusted CSVs, JSONs, or audio files can contain path traversal attacks, malformed headers, or malformed numerical data that triggers `NaN` explosions or buffer overflows.
- **Mitigation:** Validate all incoming dataset schemas, tensor shapes, and audio sampling rates at loading time before feeding them into training loops. Reject malformed inputs explicitly with a `ValueError`.

### 3. Secrets Management
- Secrets must come from environment variables or secure secret managers, never hardcoded in `src/` or configs.
- `.env.example` should be committed with placeholders; real `.env` files must be gitignored.
- Never place Hugging Face tokens, WandB API keys, or private SSH keys inside tracked files or `README.md`.

### 4. Dependency & Environment Hardening
- Machine learning repositories pull extensive transitive dependencies (CUDA binaries, PyTorch, Hugging Face ecosystem).
- Run environment and package scans after dependency modifications:
```shell
  pixi run -e safe scan_envs
```
- Pin dependency versions strictly inside `pixi.toml` / `pyproject.toml` to prevent supply-chain poisoning.


## Review Checklist

Before signing off on a PR or model integration:

[ ] Model weights scanned via `pixi run -e safe scan_model`
[ ] Virtual environment scanned via `pixi run -e safe scan_envs`
[ ] No secrets, API keys, or tokens present in code, configs, or git history
[ ] Dataset input loaders validate tensor shapes, dtypes, and boundary ranges
[ ] Checkpoints loaded securely (weights_only=True or safetensors)
[ ] No hardcoded paths, proxies, or GPU restrictions in tracked documentation

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "It's just an official checkpoint from Hugging Face, no need to scan" | Even popular repositories can be targeted or compromised; scanning takes seconds and prevents arbitrary code execution. |
| "PyTorch `torch.load` is safe because I trust the source file" | Pickle deserialization is inherently unsafe against tampering or compromised storage buckets. Use `safetensors` or `weights_only=True`. |
| "It's just a local training script, secrets don't matter" | Hardcoded tokens easily leak into shell history, error logs, or accidental public commits. |
| "Data validation slows down dataset loading" | Validating shapes and catching corrupt samples early prevents multi-hour training runs from failing halfway through due to NaN losses. |

## Red Flags

- Using `torch.load()` on unverified checkpoints without `weights_only=True` or `safetensors`
- Hardcoded API tokens or Hugging Face access keys in Python files or YAML configs
- Datasets loading external files without shape, schema, or type validation
- Missing lockfiles (`pixi.lock`) or unpinned dependency versions
- Committing `.env` files or model weights directly into Git history

## Verification

After implementing security controls:

[ ] Model weight scan passes cleanly without warnings
[ ] Environment scan passes without unmitigated vulnerability flags
[ ] Dataset loaders gracefully handle malformed or out-of-bound inputs
[ ] All API keys and credentials successfully isolated to environment variables
