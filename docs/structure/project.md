# Project

Sections of the repository. `README.md` has the short tree. The lists below are the files and the headings in the docs that follow this folder.

## Root files

- `README.md` is the start page. Its sections are Getting started, Project structure, and Organizing your research.
- `AGENTS.md` is a link to `.agents/AGENTS.md`.
- `pyproject.toml` holds the package, Pixi, and tool settings. Its sections are in `docs/structure/pyproject.md`.
- `prek.toml` holds the git hooks. Its sections are in `docs/structure/prek.md`.
- `pixi.lock` is the locked environment.
- `Dockerfile` is the image, based on the Pixi image. It installs the lockfile and then copies the tree.
- `LICENSE` is the license.
- `.env.example` lists environment variable names.
- `.gitignore` lists ignored paths. Contents of `logs/`, `datasets/`, and `weights/` are ignored.
  `configs/`, `docs/`, `scripts/`, and `src/` keep only their YAML, Markdown, shell, and Python files.
- `.markdownlint.yaml` sets the Markdown rules used by the prek hook.
- `.yamllint` sets the YAML rules used by the prek hook.

## .agents

`AGENTS.md` is the instruction file for coding agents.
`skills/` holds the playbooks those agents load: experiment launch, code review, refactor, research notes,
paper drafting, documentation, checklists, commits, security, anonymization, and competitor analysis.

## .devcontainer

A VS Code dev container. `Dockerfile` builds it.
`.devcontainer.json` selects the Python and Ruff extensions and installs the Pixi environment.
`README.md` points at the Pixi dev-container guide.

## .github

GitHub metadata and CI.

- `workflows/ci.yml` runs prek and zizmor on `ubuntu-latest`.
- `requirements-cpu.txt` is the CPU environment that job installs for Pyrefly.
- `dependabot.yml` groups action updates.
- `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`, `SECURITY.md`, `pull_request_template.md`, and `ISSUE_TEMPLATE/` are the repository texts.

## configs

Hydra configs. `main.yaml` composes `paths`, `model`, `criterion`, `optimizer`, `scheduler`, `datamodule`,
`metrics`, `lightning_module`, `callbacks`, `logger`, `checkpoint_io`, `trainer`, and `hydra`.
It also sets `seed`, `exp_name`, `num_classes`, `in_features`, and `ckpt_path`.

- `callbacks` has `common`, `early_stopping`, and `checkpointer`.
- `checkpoint_io` has the split checkpoint plugin.
- `criterion` has cross-entropy.
- `datamodule`, `lightning_module`, `metrics`, `model`, `optimizer`, `paths`, `scheduler`, and `trainer` each have a `default` config.
- `hydra` sets the run and sweep directories to `exp_name` plus the time.
- `logger` has the CSV logger.

## datasets

Local data. Git does not track the files inside this directory.

## docs

Notes. Headings in each file:

- `usecase.md`: Current configuration, How to improve.
- `another_template.md`: Versions, Differences, Safety. Safety contains Code safety and Model loading safety.
- `ai-ethics/reforms-framework.md`: Study Goals, Computational reproducibility, Data quality, Data preprocessing,
  Modeling, Data leakage, Metrics and uncertainty, Generalizability and limitations.
- `ai-ethics/fair-principles.md`: Findable, Accessible, Interoperable, Reusable.
- `ai-ethics/open-ethics-canvas.md`: Canvas Metadata, Canvas Topics & Evaluation Checklist.
- `structure/prek.md`, `structure/project.md`, and `structure/pyproject.md` are this folder.
  Their headings match the sections of `prek.toml`, this tree, and `pyproject.toml`.

## logs

Hydra and Lightning output. Git does not track the files inside this directory.

## notebook

Jupyter notebooks. The `nb-clean` hook removes empty cells and keeps outputs.

## scripts

- `setup.sh` asks for a first name, a second name, and an optional email, writes them into `pyproject.toml`, and runs `pixi install`.
- `wait_gpu.sh` waits until a process exits or a GPU is idle, then starts the given command with `pixi`.

## src

Experiment code.

- `train.py` runs training. A set `ckpt_path` resumes weights, optimizer state, and epoch.
- `eval.py` loads checkpoint weights and writes `test_metrics.json` into that checkpoint directory.
- `data` has the dataset and the Lightning datamodule.
- `model` has the network and the Lightning module.
- `plugins` has the split checkpoint plugin.
- `utils` has `checkpoint.py`, `logger.py`, `metrics.py`, and `trainer.py`.

## tests

Pytest modules for data, the model, the checkpoint plugin, utils, and evaluation. `pythonpath` is `src`.

## weights

Local model weights. Git does not track the weight files.
