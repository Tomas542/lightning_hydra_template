---
name: ai-checklist
description: 'Checklisting of current project with different community lists.'
---
# AI checklist for ML Research

## Overview

Comprehensive AI & Research Compliance Checklist, that saves results to `docs/ai-checklist.md`. This compliance checklist integrates **FAIR** data stewardship, the **REFORMS** framework for robust machine learning, and the complete **Open Ethics Canvas** framework into a single executable workflow for machine learning research repositories.

## When to Use

Use this skill when:

- All works with code are finished or close to be finished and it is time to prepare a paper draft.
- There is a need to verify, that code or research are follow community standards.

## 1. FAIR Principles (Data & Model Management)
*Ensure datasets, models, code, and supplementary artifacts are discoverable, accessible, interoperable, and reusable.*

### Findable (F) - Data and metadata should be easy to find for both humans and computers.
- F1. (Meta)data are assigned a globally unique and persistent identifier.
- F2. Data are described with rich metadata (defined by R1 below).
- F3. Metadata clearly and explicitly include the identifier of the data it describes.
- F4. (Meta)data are registered or indexed in a searchable resource.

### Accessible (A) - Once found, data should be retrievable through standardized protocols.
- A1. (Meta)data are retrievable by their identifier using a standardized communications protocol.
    - A1.1 The protocol is open, free, and universally implementable.
    - A1.2 The protocol allows for an authentication and authorization procedure, where necessary.
- A2. Metadata are accessible, even when the data are no longer available.

### Interoperable (I) - Data should be able to be integrated with other data and work with applications for analysis.
- I1. (Meta)data use a formal, accessible, shared, and broadly applicable language for knowledge representation.
- I2. (Meta)data use vocabularies that follow FAIR principles.
- I3. (Meta)data include qualified references to other (meta)data.

### Reusable (R) - Data should be well-described so it can be replicated and/or combined in different settings.
- R1. Meta(data) are richly described with a plurality of accurate and relevant attributes.
    - R1.1. (Meta)data are released with a clear and accessible data usage license.
    - R1.2. (Meta)data are associated with detailed provenance.
    - R1.3. (Meta)data meet domain-relevant community standards.

---

## 2. REFORMS Framework (Robust & Reliable ML Science)

*Minimize methodology errors, false scientific claims, data leakage, and evaluation flaws in ML research.*

### Study Goals

- 1a. Population, distribution or real-world domain about which the scientific claim is made.
- 1b. Motivation for choosing this population or distribution (1a.). why the chosen dataset faithfully represents the target population without unmanaged sample selection bias.
- 1c. Motivation for the use of ML methods in the study.

### Computational reproducibility

- 2a. Dataset used for training and evaluating the model along with link or DOI to uniquely identify the dataset.
- 2b. Code used to train and evaluate the model and produce the results reported in the paper along with link or DOI to uniquely identify the version of the code used.
- 2c. Description of the computing infrastructure used.
    - Hardware infrastructure: CPU, GPU, RAM, disk space etc.
   â- Operating system.
    - Software environment: Programming language and version, documentation of all packages used along with versions and dependencies (e.g., through a requirements.txt file).
    - An estimate of the time taken to generate the results.
- 2d. README file which contains instructions for generating the results using the provided dataset and code.
- 2e. Reproduction script to produce all results reported in the pape

### Data quality

- 3a. Source(s) of data, separately for the training and evaluation datasets (if applicable), along with the time when the dataset(s) are collected, the source and process of ground-truth annotations, and other data documentation.
- 3b. Distribution or set from which the dataset is sampled (i.e., the sampling frame).
- 3c. Justification for why the dataset is useful for the modeling task at hand.
- 3d. The definition of the outcome variable of the model along with descriptive statistics, if applicable. (The outcome variable is also known as the dependent variable, the target variable, the output variable or the predicted variable).
- 3e. Number of samples in the dataset.
- 3f. Percentage of missing data, split by class for a categorical outcome variable.
- 3g. Justification for why the distribution or set from which the dataset is drawn (3b.) is representative of the one about which the scientific claim is being made (1a.).

### Data preprocessing

- 4a. Identification of whether any samples are excluded with a rationale for why they are excluded.
- 4b. How impossible or corrupt samples are dealt with.
- 4c. All transformations of the dataset from its raw form (3a.) to the form used in the model, for instance, treatment of missing data and normalization.

### Modeling

- 5a. Detailed descriptions of all models trained, including:
    - All features used in the model (including any feature selection).
    - Types of models implemented (e.g., Random Forests, Neural Networks).
    - Loss function used.
- 5b. Justification for the choice of model types implemented.
- 5c. Method for evaluating the model(s) reported in the paper, including details of train-test splits or cross-validation folds.
- 5d. Method for selecting the model(s) reported in the paper.
- 5e. For the model(s) reported in the paper, specify details about the hyperparameter tuning:
    - Range of hyper-parameters used and a justification for why this range is reasonable.
    - Method to select the best hyper-parameter configuration.
    - Specification of all hyper-parameters used to generate results reported in the paper.
- 5f. Justification that model comparisons are against appropriate baselines.

### Data leakage

- 6a. Justification that pre-processing (Section 4) and modeling (Section 5) steps only use information from the training dataset (and not the test dataset).
- 6b. Methods to address dependencies or duplicates between the training and test datasets (e.g. different samples from the same patients are kept in the same dataset partition).
- 6c. Justification that each feature or input used in the model is legitimate for the task at hand and does not lead to leakage.

### Metrics and uncertainty

- 7a. All metrics used to assess and compare model performance (e.g., accuracy, AUROC etc.). Justify that the metric used to select the final model is suitable for the task.
- 7b. Uncertainty estimates (e.g., confidence intervals, standard deviations), and details of how these are calculated.
- 7c. Justification for the choice of statistical tests (if used) and a check for the assumptions of the statistical test.

### Generalizability and limitations

- 8a. Evidence of external validity.
- 8b. Contexts in which the authors do not expect the study's findings to hold.

---

3. Open Ethics Canvas
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
