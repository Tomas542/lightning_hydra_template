# REFORMS Framework (Robust & Reliable ML Science)

Minimize methodology errors, false scientific claims, data leakage, and evaluation flaws in ML research.
[Link](https://reforms.cs.princeton.edu/).

## Study Goals

- 1a. Population, distribution or real-world domain about which the scientific claim is made.
- 1b. Motivation for choosing this population or distribution (1a.). why the chosen dataset faithfully represents the target population without unmanaged sample selection bias.
- 1c. Motivation for the use of ML methods in the study.

## Computational reproducibility

- 2a. Dataset used for training and evaluating the model along with link or DOI to uniquely identify the dataset.
- 2b. Code used to train and evaluate the model and produce the results reported in the paper along with link or DOI to uniquely identify the version of the code used.
- 2c. Description of the computing infrastructure used.
    - Hardware infrastructure: CPU, GPU, RAM, disk space etc.
   �- Operating system.
    - Software environment: Programming language and version, documentation of all packages used along with versions and dependencies (e.g., through a requirements.txt file).
    - An estimate of the time taken to generate the results.
- 2d. README file which contains instructions for generating the results using the provided dataset and code.
- 2e. Reproduction script to produce all results reported in the pape

## Data quality

- 3a. Source(s) of data, separately for the training and evaluation datasets (if applicable), along with the time when the dataset(s) are collected, the source and process of ground-truth annotations, and other data documentation.
- 3b. Distribution or set from which the dataset is sampled (i.e., the sampling frame).
- 3c. Justification for why the dataset is useful for the modeling task at hand.
- 3d. The definition of the outcome variable of the model along with descriptive statistics, if applicable. (The outcome variable is also known as the dependent variable, the target variable, the output variable or the predicted variable).
- 3e. Number of samples in the dataset.
- 3f. Percentage of missing data, split by class for a categorical outcome variable.
- 3g. Justification for why the distribution or set from which the dataset is drawn (3b.) is representative of the one about which the scientific claim is being made (1a.).

## Data preprocessing

- 4a. Identification of whether any samples are excluded with a rationale for why they are excluded.
- 4b. How impossible or corrupt samples are dealt with.
- 4c. All transformations of the dataset from its raw form (3a.) to the form used in the model, for instance, treatment of missing data and normalization.

## Modeling

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

## Data leakage

- 6a. Justification that pre-processing (Section 4) and modeling (Section 5) steps only use information from the training dataset (and not the test dataset).
- 6b. Methods to address dependencies or duplicates between the training and test datasets (e.g. different samples from the same patients are kept in the same dataset partition).
- 6c. Justification that each feature or input used in the model is legitimate for the task at hand and does not lead to leakage.

## Metrics and uncertainty

- 7a. All metrics used to assess and compare model performance (e.g., accuracy, AUROC etc.). Justify that the metric used to select the final model is suitable for the task.
- 7b. Uncertainty estimates (e.g., confidence intervals, standard deviations), and details of how these are calculated.
- 7c. Justification for the choice of statistical tests (if used) and a check for the assumptions of the statistical test.

## Generalizability and limitations

- 8a. Evidence of external validity.
- 8b. Contexts in which the authors do not expect the study's findings to hold.
