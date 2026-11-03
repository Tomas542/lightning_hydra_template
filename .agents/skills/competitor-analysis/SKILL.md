---
name: competitor-analysis
description: Discovers, evaluates, and ranks state-of-the-art ML methods from research papers (via AlphaXiv MCP) to establish competitive baselines or hackathon solution candidates. Filters papers by release date and code availability.
---

# Competitor & Baseline Analysis

## Overview

Identify top-performing methodologies, baseline models, and algorithmic competitors for a specified task or domain. This skill leverages the AlphaXiv MCP server to query recent research within specific date ranges, analyze method trade-offs, inspect repository codebases, and compile a structured comparison list.

## When to Use

- Preparing for a machine learning competition or hackathon
- Establishing baseline methods for a new research proposal
- Auditing recent advances (e.g., past 6 to 12 months) in a target subfield
- Extracting open-source code references associated with recent papers

---

## Workflow Protocol

### Step 1: Define Search Bounds & Temporal Constraints
Determine the exact task parameters, evaluation metrics, and target date range.
- Default to searching papers published within the last 12 months unless a specific `published_after` date is provided.
- Format dates strictly as `YYYY-MM-DD`.

### Step 2: Query Research via AlphaXiv MCP
Execute paper discovery using AlphaXiv MCP tools:
1. Call `discover_papers` with:
   - `query`: A detailed semantic description of the task, target metrics, and desired architecture features.
   - `published_after`: `YYYY-MM-DD` limit.
   - `published_before`: `YYYY-MM-DD` (optional bound).
   - `difficulty`: Set between 5–8 for deep iterative search across candidate literature.
2. Filter results for:
   - High metric relevance to the target task.
   - Associated official GitHub/code repositories.

### Step 3: Analyze Candidate Methods
For top-ranked candidate papers:
1. Retrieve full paper context via AlphaXiv `read_paper` / `get_paper_details`.
2. Inspect linked repository structures using `read_paper_codebase` to verify implementation feasibility, library dependencies, and pretrained weight availability.
3. Evaluate each method across four criteria:
   - **Performance:** SOTA metrics on public benchmarks.
   - **Complexity & Latency:** Computational footprint and training/inference speed.
   - **Implementation Effort:** Time required to adapt or re-use code during a short timeline/hackathon.
   - **Licensing & Dependencies:** Open-source software licenses and environment compatibility (`pixi` / `uv`).

### Step 4: Record & Structure Findings
Log candidate methods into `docs/notes/competitor-methods.md` using the standardized candidate template.

---

## Verification & Output Checklist

When compiling candidate baselines, ensure each entry includes:
- [ ] Universal paper ID / arXiv identifier and official paper title
- [ ] Publication date (verified within the target range)
- [ ] Core algorithmic innovation (1–2 sentences)
- [ ] Link to official code repository
- [ ] Feasibility rating for quick integration (High / Medium / Low)
