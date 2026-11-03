---
name: anonymization
description: Sanitizes repository code, paths, comments, and documentation before supplementary material submission or public open-sourcing. Scans for absolute paths, replaces them with placeholders, updates README configuration notes, logs non-anonymous entities (nicknames, non-English comments) in ANON.md, and handles supplementary `.git` removal notices.
---

# Repository Anonymization & De-identification

## Overview

A systematic procedure for preparing a research repository for peer-review supplementary material submission or public release. This skill ensures compliance with double-blind review guidelines and data privacy standards by purging system-specific paths, personal identifiers, internal cluster references, and non-English commentary.

## When to Use

- **Supplementary Submission:** Preparing a `.zip` or archive for double-blind conference review (e.g., ICLR, Interspeech, NeurIPS).
- **Public Open-Sourcing:** Transitioning a private enterprise or laboratory repository to a public GitHub/GitLab organization.

---

## Execution Workflow

### Step 1: Determine Anonymization Mode

Ask or confirm the target mode:
1. **`supplementary` Mode:** Scans **every** file in the repository (including untracked files, local configs, and build outputs). Prepares notes for removing the `.git` directory.
2. **`public` Mode:** Scans only **Git-tracked** files (`git ls-files`) to avoid leaking uncommitted scratch work, leaving `.git` intact.

Verify from the user, whether they need to submit `logs/`. In case of yes, remove configs and files with metrics from `.gitignore`.

---

### Step 2: Absolute Path Scanning & Replacement

1. **Scan for Hardcoded Absolute Paths:**
   - Linux/macOS paths: `/home/username/`, `/Users/username/`, `/mnt/`, `/nfs/`, `/scratch/`, `/data/`
   - Windows paths: `C:\Users\`, `D:\`
   - Internal server IPs, cluster paths, or absolute virtual environment prefixes.
2. **Replace with Placeholders:**
   - Replace absolute paths in code, configuration files (`pyproject.toml`, `pixi.toml`, Hydra configs in `configs/`), and scripts with clear, parameterized placeholders:
     - Data directories: `<PATH_TO_DATA>` or `${DATA_ROOT}`
     - Checkpoint/Output directories: `<PATH_TO_CHECKPOINTS>` or `${CHECKPOINT_DIR}`
     - Home/Workspace roots: `<WORKSPACE_ROOT>`

---

### Step 3: Update `README.md` (Getting Started / Setup)

- Locate the **Getting Started** or **Configuration** section of `README.md`.
- Add a dedicated subsection instructing users how to configure their local environment paths:

```markdown
### Environment Configuration
Before running training or evaluation scripts, update the placeholder paths in your configuration files or environment variables:
- `DATA_ROOT`: Point to your local dataset directory.
- `CHECKPOINT_DIR`: Point to your model weight storage directory.
```

### Step 4: Audit Non-Anonymous Entities (ANON.md)

Create or update ANON.md in the root of the project to document entities that require manual review or cleanup before publication:

- **Nicknames & Personal Names:** Authors, lab members, or system usernames found in code comments, docstrings, or commit logs.
- **Non-English Comments:** Comments, debug logs, or documentation written in local languages (e.g., Russian, Chinese) that should either be translated to English or scrubbed for anonymous review.
- **Internal URLs / Endpoints:** Proprietary intranet links, internal slack channels, or private API endpoints.

`ANON.md` Template Structure

```markdown
# Anonymization & Review Log

The following items were identified during the automated repository audit and require manual verification or removal before final publication:

## 1. Non-English Comments / Localized Text

- [ ] `src/data/loader.py:45` — Comment in Cyrillic: `# TODO: дописать проверку сэмплов`
- [ ] `src/models/audio.py:112` — Log message in local language

## 2. Personal Identifiers & Nicknames

- [ ] `configs/train.yaml:12` — Author username found in default logging path (`/home/artem/`)

## 3. Internal Endpoints / Infrastructure

- [ ] `scripts/submit.sh:8` — Internal cluster scheduler address (`slurm.internal.lab`)
```

### Step 5: Supplementary Submission Safeguards (If Applicable)

If running in supplementary mode:

- Add a prominent notice at the very beginning of `README.md`:
- Important Notice for Reviewers: This archive has been stripped of its `.git` history to ensure double-blind review compliance.

Verify that the `.git` folder is excluded or provide explicit shell commands for the user to delete it before packaging:

```shell
rm -rf .git .gitignore .github/
```

## Verification Checklist

Before finalizing the package or push:

- [ ] All absolute system paths replaced with environment variables or clear placeholders (`<...>`)
- [ ] README.md updated with setup instructions for configuring paths
- [ ] `ANON.md` created in root and populated with flagged nicknames, comments, and internal links
- [ ] (Supplementary Mode) `.git` directory removal instructions or execution verified
