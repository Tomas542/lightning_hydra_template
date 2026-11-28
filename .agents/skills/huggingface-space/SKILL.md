---
name: huggingface-space
description: Creates, tests, and deploys an interactive research results demo (using Gradio or Streamlit) to a Hugging Face Space. Configures metadata frontmatter, handles dependencies, and pushes assets to the Hub.
---

# Publish Research Demo to Hugging Face Space

## Overview

Deploy interactive model checkpoints, visualization notebooks, or quantitative evaluation results as a live web application on Hugging Face Spaces. This skill standardizes the creation of `app.py`, `README.md` metadata (YAML frontmatter), dependency management, and git push workflows to HF Hub.

## When to Use

- Presenting qualitative or quantitative research results from a paper or hackathon project.
- Sharing an interactive model checkpoint demo.
- Creating a reproducible web frontend for reviewers or the public.

---

## Execution Workflow

### Step 1: Choose Framework & Define UI Scope
Prepare an app with gradio. This is recommended for ML model inference, audio processing demos (using `librosa` / PyTorch), and interactive sliders.

### Step 2: Prepare Space Configuration & Metadata (`README.md`)
Every Hugging Face Space requires a YAML frontmatter header inside its root `README.md` to configure the runtime. Create or verify the header:

```yaml
---
title: "Project Name Demo"
emoji: "🚀"
colorFrom: "blue"
colorTo: "purple"
sdk: "gradio"
sdk_version: "4.40.0"
app_file: "app.py"
pinned: false
license: "mit"
---
```
### Step 3: Bundle Dependencies
Ensure a lightweight requirements file or Pixi export is included so the Space builds successfully:
- Create requirements.txt listing essential runtime libraries (e.g., `gradio`, `torch`, `librosa`, `pandas`).
- Keep heavy model weights hosted separately on the Hugging Face Model Hub rather than bloating the git repository; download them dynamically on startup inside `app.py` using huggingface_hub.

### Step 4: Initialize and Push to Hugging Face
- Verify authentication: Ensure the user has logged in via `huggingface-cli` login or set `HF_TOKEN`.
- Create the remote Space (if not already created via web interface):

```shell
huggingface-cli repo create <space-name> --type space --space_sdk gradio
```

Clone, link, and push the demo directory:

```shell
git remote add hf [https://huggingface.co/spaces/](https://huggingface.co/spaces/)<username>/<space-name>
git push hf main --force
```

## Verification & Output Checklist
[ ] `app.py` successfully runs locally without missing imports or hardcoded local absolute paths.
[ ] `README.md` contains valid YAML frontmatter matching the chosen SDK (gradio).
[ ] `requirements.txt` or configuration files are present for container build execution.
[ ] Live Space URL is verified and functional after pushing.
[ ] Space is for CPU basic tier without GPU.
