---
name: idea-roast
description: Adversarially critiques, stress-tests, and exposes fatal flaws in ML research ideas, model architectures, experimental designs, or hackathon pitches before implementation begins. Acts as a ruthless Reviewer #2 and pragmatic senior engineer.
---

# Adversarial Idea Roast & Stress-Test

## Overview

Subject a proposed research hypothesis, architectural modification, dataset strategy, or hackathon solution to an uncompromising, evidence-based critique. The goal is to kill weak ideas early, uncover hidden assumptions, prevent wasted compute, and expose Reviewer #2 objections before writing code.

## When to Use

- Before starting a new research project, thesis chapter, or conference submission.
- Evaluating whether a proposed model modification is actually novel or just incremental noise.
- Pressure-testing a hackathon pitch for feasibility, latency, and evaluation traps.
- Preparing rebuttal defenses by anticipating the harshest possible peer-review criticisms.

---

## Execution Workflow

### Step 1: Parse the Pitch & Strip the Hype
Extract the core claim from the user's idea without marketing fluff:
- **The Bet:** What exact mechanism is supposed to drive performance gains?
- **The Baseline:** What simpler method already solves 90% of this problem?
- **The Cost:** What extra compute, data, or engineering complexity does this introduce?

### Step 2: Run the 5-Axis Adversarial Audit
Evaluate the idea across five failure dimensions:

1. **The "Reviewer #2" Novelty & Delta Check**
   - Is this genuinely a new insight, or just slapping two existing modules together (e.g., *"X + Attention"*)?
   - If the proposed novelty is removed (ablation), does the baseline perform nearly identically?
   - Has this already been solved or disproven in adjacent literature? *(Optionally cross-check recent literature via AlphaXiv MCP if configured).*

2. **Data Leakage & Evaluation Mirage**
   - Are the proposed metrics actually measuring the claimed capability, or can a trivial shortcut/spurious correlation game the benchmark?
   - Does the train/val/test split risk subtle leakage (e.g., speaker overlap, channel artifacts, temporal leakage, or pretraining contamination)?

3. **The Simple Baseline Trap (Occam's Razor)**
   - Would better data augmentation, hyperparameter tuning, or a larger pretrained backbone beat this complex architecture in half the time?
   - Is the engineering complexity justified by realistic expected gains?

4. **Compute, Latency & Scaling Bottlenecks**
   - Where does this blow up in memory, training instability (gradient explosion, collapse), or inference latency?
   - Can it actually be trained and iterated on within available hardware and timeline constraints?

5. **Real-World & Robustness Failure Modes**
   - What happens under distribution shift, noisy inputs, edge cases, or adversarial perturbations?
   - Does it violate any methodological or ethical sanity checks (refer to `docs/ethics/reforms-framework.md` if present)?

### Step 3: Deliver the Roast & Survival Plan
Structure the critique candidly—direct, sharp, and technically grounded, never vague or overly polite:
1. **The Brutal Verdict (TL;DR):** One paragraph summarizing the single biggest reason this idea could fail or get desk-rejected.
2. **Fatal Flaws & Blind Spots:** Bullet-point breakdown of the hardest technical, experimental, and novelty weaknesses.
3. **The "Do This First" Kill-Test:** One minimal, fast falsification experiment (e.g., a 1-hour toy test or strict ablation) that will prove whether the core hypothesis actually holds before building the full pipeline.
4. **How to Salvage It:** Concrete pivots or scope reductions that turn the weak points into defensible contributions.

---

## Verification Checklist

- [ ] Critique directly targets technical mechanics, assumptions, and experimental validity (no generic filler praise).
- [ ] At least one simpler baseline or ablation alternative is explicitly proposed.
- [ ] Evaluation traps, shortcut learning risks, or compute bottlenecks are identified.
- [ ] A concrete, low-cost falsification experiment ("kill-test") is defined.
