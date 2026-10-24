---
name: paper-drafting
description: Use when formatting experiment results into publication-ready LaTeX tables, drafting methodology sections, or generating formal research reports.
---

# Paper Drafting & LaTeX Formatting

This skill converts experimental outcomes, dataset statistics, and model architectures into publication-ready LaTeX code and structured technical write-ups.

## 1. Formatting LaTeX Tables
When generating tables for reports or paper drafts, follow standard academic LaTeX style:
- Use `booktabs` (`\toprule`, `\midrule`, `\bottomrule`).
- Avoid vertical borders (`|`).
- Explicitly bold the best metric result in each column and underline the second-best result (unless instructed otherwise).
- Wrap numbers and metric uncertainties cleanly.
- Add up and down arrow keys near the metrics' names.

### Standard LaTeX Table Template:
```latex
\begin{table}[htbp]
\centering
\caption{\textbf{Model Evaluation Results.} Short caption describing the baseline vs. proposed setup.}
\label{tab:main_results}
\begin{tabular}{lcccc}
\toprule
\textbf{Model} & \textbf{Params (M)} & \textbf{Val Loss $\downarrow$} & \textbf{Accuracy ($\%$) $\uparrow$} & \textbf{Latency (ms)} \\
\midrule
Baseline Transformer & 110.4 & 0.421 & 88.4 & 12.3 \\
Proposed Variant     & 112.1 & \textbf{0.389} & \textbf{90.1} & 13.1 \\
\bottomrule
\end{tabular}
\end{table}
```
## 2. Text & Claims Directives
- Factual Fidelity: Every quantitative claim made in text must match documented metrics from research-notes/ or raw log files.
- Tone: Use objective, precise academic language (e.g., "Our experiments demonstrate a 1.7% increase in validation accuracy" instead of "Our amazing model outperforms everything").
- LLM pitfalls: do not use common LLM generated text patterns (—, excessive boldface, citation style quirks)
- Notation: Define mathematical notation cleanly using LaTeX syntax (e.g., $L_{\text{total}} = L_{\text{ce}} + \lambda L_{\text{reg}}$).

## 3. Workflow for Outputting Drafts
- Pull verified metrics from the logged run notes.
- Output LaTeX tables or LaTeX snippet blocks directly in markdown code fences (`latex`) so they can be easily copied to target documents.
- Verify that column alignment keys match the number of header columns.
