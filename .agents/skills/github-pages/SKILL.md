---
name: github-pages
description: Builds, configures, and deploys a static research project page or documentation site to GitHub Pages. Sets up static assets, audio/visual demo players, citation blocks, and automated GitHub Actions deployment workflows.
---

# Publish Research Project Page to GitHub Pages

## Overview

Deploy a static academic project page, interactive media showcase (e.g., audio samples, spectrograms, comparison tables), or documentation portal directly from the repository using GitHub Pages. This skill standardizes the site structure, static media asset organization, citation embedding, and automated CI/CD deployment via GitHub Actions.

## When to Use

- Creating an academic project landing page for a conference paper (e.g., Interspeech, ICLR, NeurIPS).
- Hosting static audio/visual qualitative comparisons (e.g., real vs. synthetic speech samples, watermarked audio comparisons) that do not require live GPU inference.
- Publishing automated documentation or experiment reports from `docs/`.
- Providing a central hub linking to the arXiv paper, GitHub code, Zenodo DOI, and live Hugging Face Space demo.

---

## Execution Workflow

### Step 1: Select Static Site Architecture
Prepare a plan to structure research as **Academic Project Landing Page (`index.html`)**. It is the best for paper showcases. Uses a clean single-page layout (e.g., Bulma/Academic Project Page template) featuring the abstract, architecture diagram, interactive HTML5 `<audio>`/`<video>` comparison grids, and BibTeX block.

### Step2: Organize Static Assets & Media
Store all web assets in a dedicated directory (`site/`) to keep the repository root clean:
- Place lightweight media samples (`.wav`, `.mp3`, `.png`, `.svg`) in `site/static/media/`.
- Compress large audio/image files so the repository size stays small and page load times remain fast.
- Ensure all asset references in HTML/Markdown use **relative paths** (e.g., `./static/media/sample_01.wav`) rather than root-relative paths (`/static/...`), as GitHub Pages serves project sites from a subpath (`https://<username>.github.io/<repo-name>/`).

### Step 3: Embed Academic Metadata & Cross-Links
Ensure the landing page includes standard scholarly components:
- **Action Buttons:** Direct links to Paper (arXiv), Code (GitHub), Archive (Zenodo DOI), and Interactive Demo (Hugging Face Space).
- **Citation Section:** Mirror the repository's `CITATION.cff` / `README.md` BibTeX snippet inside a copyable `<pre><code>` block.
- **Open Graph / Meta Tags:** Add title, description, and preview image tags in `<head>` for clean link previews on social media and Slack.

### Step 4: Configure GitHub Actions Deployment (`.github/workflows/pages.yml`)
Automate deployment on every push to `main` using official GitHub Pages actions:

```yaml
name: Deploy GitHub Pages

on:
  push:
    branches: ["main"]
  workflow_dispatch:

permissions:
  contents: read
  pages: write
  id-token: write

concurrency:
  group: "pages"
  cancel-in-progress: false

jobs:
  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
      - name: Setup Pages
        uses: actions/configure-pages@v5
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: "./site" # Adjust to "./docs" or build output directory if using MkDocs
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
```

## Step 5: Enable Pages in Repository Settings
1. Push `.github/workflows/pages.yml` and the `site/` directory to GitHub.
2. Navigate to Repository Settings -> Pages -> Build and deployment.
3. Set Source to GitHub Actions.
4. Verify the live deployment URL at `https://<username>.github.io/<repo-name>/`.

## Verification & Output Checklist
[ ] All media assets, stylesheets, and scripts load correctly using relative paths (./...).
[ ] Audio/visual demo players work across browsers without broken links or oversized files.
[ ] BibTeX citation block matches CITATION.cff and README.md.
[ ] `.github/workflows/pages.yml` passes CI without permission or artifact path errors.
[ ] Live GitHub Pages URL is accessible and added to the repository's GitHub "About" website field and `README.md`.
