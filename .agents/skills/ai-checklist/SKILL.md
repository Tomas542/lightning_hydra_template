---
name: ai-checklist
description: 'Checklisting of current project with different community lists.'
---
# Comprehensive AI & Research Compliance Checklist (`docs/ai-checklist.md`)

This compliance checklist integrates **FAIR** data stewardship, the **REFORMS** framework for robust machine learning, and the complete **Open Ethics Canvas** framework into a single executable workflow for machine learning research repositories.

## 1. FAIR Principles (Data & Model Management)
*Ensure datasets, models, code, and supplementary artifacts are discoverable, accessible, interoperable, and reusable.*

### Findable (F)
- [ ] **Persistent Identifiers (PIDs):** Datasets, code checkpoints, and trained models are assigned globally unique and persistent identifiers (e.g., DOIs, Hugging Face Hub repositories, or pinned versioned git hashes).
- [ ] **Rich Metadata Bundles:** Metadata describing the artifact (creators, abstract, versioning tags, and release dates) is packaged alongside the release.
- [ ] **Searchable Index Registration:** Metadata is indexed in an open repository or registry (e.g., Zenodo, institutional dataverse, or Hugging Face Hub).

### Accessible (A)
- [ ] **Standard Open Protocols:** Metadata and raw data/model assets are retrievable via standardized, open communication protocols (HTTP, HTTPS, Git, S3).
- [ ] **Authenticated Access Rules:** Where data access must be restricted (e.g., PII, sensitive speech, restricted medical records), clear authorization and access request workflows are documented.

### Interoperable (I)
- [ ] **Standard Interchange Formats:** Code, model weights, and data files utilize open, standardized formats (e.g., `safetensors`, `ONNX`, Parquet, JSON, CSV).
- [ ] **Qualified Cross-References:** Artifacts include explicit version linkages and dependency references to underlying base models, packages, and datasets.

### Reusable (R)
- [ ] **Detailed Provenance & Lineage:** Data collection protocols, cleaning scripts, filtering parameters, and labeling guidelines are comprehensively logged in `docs/notes/`.
- [ ] **Permissive Research Licensing:** Code, models, and datasets are released under clear open-source licenses (e.g., MIT, Apache 2.0, CC-BY 4.0).
- [ ] **Community Standards Alignment:** Data structures and evaluation schemes adhere strictly to established domain conventions.

---

## 2. REFORMS Framework (Robust & Reliable ML Science)
*Minimize methodology errors, false scientific claims, data leakage, and evaluation flaws in ML research.*

### Study Goals & Population
- [ ] **Target Population Definition:** Explicitly defines the specific population, distribution, or real-world domain about which the scientific claim is made.
- [ ] **Representativeness Justification:** Documents why the chosen dataset faithfully represents the target population without unmanaged sample selection bias.

### Data Quality & Preprocessing
- [ ] **Data Provenance Logged:** Details precisely when, where, and how raw data were gathered, alongside human annotation criteria.
- [ ] **Sampling Boundaries:** Outlines sample inclusion/exclusion boundaries.
- [ ] **Strict Leakage Prevention:** Verifies that data preprocessing steps (scaling, mean/variance normalization, tokenization, audio resampling, data augmentation) are computed **strictly** on training splits *after* splitting—preventing test data leakage.

### Modeling & Evaluation Rigor
- [ ] **Specification of Architecture & Search:** Main modeling choices, architecture modifications, and hyperparameter search spaces are formalized via Hydra configs (`configs/`).
- [ ] **Uncertainty & Variance Quantification:** Reports performance variance, confidence intervals, and training stability measures across multiple random seeds.
- [ ] **Out-of-Sample Evaluation:** Evaluates final models exclusively on held-out test data completely isolated from training and hyperparameter tuning loops.

### Computational Reproducibility
- [ ] **Pinned Environment Consistency:** Dependencies are locked (`pixi.lock`) and verifiable via environment health checks (`scan_envs`).
- [ ] **Independent Execution Ready:** An independent researcher can reproduce training and evaluation pipelines seamlessly using repository instructions.

---

## 3. Open Ethics Canvas
*A structured framework for mapping ethical, social, safety, and operational dimensions. (Note: Specific points may be adapted or omitted depending on the exact scope and topic of the research).*

### Canvas Metadata
- **Designed for:** [Project / Research Domain / Model Name]
- **Designed by:** [Author / Researcher / Team]
- **Date:** 2026-10-26
- **Version:** 1.0

### Canvas Topics & Evaluation Checklist
- [ ] **Scope:** Define the operational boundaries, application domain, and out-of-scope constraints of the system.
- [ ] **Users:** Identify who will directly interact with or operate the model/system.
- [ ] **Key stakeholders:** Map all groups, organizations, and communities impacted indirectly or directly by the system.
- [ ] **Values & Interests:** Articulate the underlying values, ethical goals, and organizational interests shaping the project.
- [ ] **Impact Assessment:** Evaluate potential positive benefits and negative externalities on individuals and society.
- [ ] **Changes in behaviour:** Analyze how the system might alter user habits, workflows, or societal interactions.
- [ ] **Training Data:** Document the provenance, collection methods, quality, and representation of datasets used.
- [ ] **Personal Data Processing:** Audit the handling, anonymization, and minimization of PII or sensitive records.
- [ ] **Explainability:** Assess mechanisms for interpreting model decisions, attention weights, or feature attributions.
- [ ] **Group Interactions:** Evaluate how multi-agent dynamics or community-level behaviors are affected.
- [ ] **Algorithms & Source code:** Review core model architectures, optimization objectives, and source code integrity.
- [ ] **Components & Subprocessing:** Map external APIs, third-party libraries, and microservice dependencies.
- [ ] **Human in the Loop:** Specify where human oversight, intervention, or final approval is enforced.
- [ ] **Regulatory Landscape:** Verify adherence to relevant legal frameworks, compliance standards, and data protection laws (e.g., GDPR).
- [ ] **Decision Space:** Outline the permissible range of outputs, automated actions, and constraints imposed on the model.
- [ ] **Failure Modes:** Identify foreseeable technical breakdowns, hallucinations, numerical instabilities (e.g., NaN losses), or adversarial vulnerabilities.
- [ ] **Model Performance Metrics:** Define quantitative benchmarks (e.g., accuracy, F1, calibration) used to validate success.
- [ ] **Decision Feedback & Objection:** Establish channels for users or stakeholders to contest, report, or appeal automated decisions.
- [ ] **Mitigation:** Document technical and operational strategies deployed to address identified risks, biases, and failure modes.
