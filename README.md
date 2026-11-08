# And another one lightning-hydra template

You can see `docs/` folder for more information about this template, but it is still in progress

## Getting started

[Pixi](https://pixi.prefix.dev/) needs to be installed first.
From the repository root, run:

```shell
bash scripts/setup.sh
```

The script asks for your first name, second name, and an optional email, then writes them to `pyproject.toml`.
If `origin` is set, it also sets `Source` to that remote and points the existing-issues link in `.github/CONTRIBUTING.md` at it.
It then runs `pixi install`.

GitHub Actions in `.github/workflows/` are there for a public repository.
On a private repository they spend the account's Actions minutes, which are limited by the GitHub plan.
Remove `.github/workflows/` when this project is private.

## Project structure

The directory structure looks like this:

```text
├── .agents                   <- Agent instructions and skills
│   ├── skills                   <- Experiment, review, and research skills
│   └── AGENTS.md                <- Instructions for coding agents
├── .devcontainer             <- Dev container definition
├── .github                   <- GitHub Actions, Dependabot, and issue templates
├── configs                   <- Hydra configs
│   ├── callbacks                <- Callback configs
│   ├── checkpoint_io            <- Split checkpoint plugin config
│   ├── criterion                <- Loss configs
│   ├── datamodule               <- Datamodule configs
│   ├── hydra                    <- Hydra output path
│   ├── lightning_module         <- Lightning module configs
│   ├── logger                   <- Logger configs
│   ├── metrics                  <- Metric configs
│   ├── model                    <- Model configs
│   ├── optimizer                <- Optimizer configs
│   ├── paths                    <- Project path configs
│   ├── scheduler                <- Scheduler configs
│   ├── trainer                  <- Trainer configs
│   └── main.yaml                <- Main config
├── datasets                  <- Project data
├── docs                      <- Notes on the template, ethics, and repo layout
│   ├── ai-ethics                <- REFORMS, FAIR, and Open Ethics checklists
│   ├── structure                <- Sections of the repo, prek, and pyproject
│   ├── another_template.md      <- Comparison with other templates
│   └── usecase.md               <- How to adopt and tighten the template
├── logs                      <- Logs from Hydra and Lightning
├── notebook                  <- Jupyter notebooks
├── scripts                   <- Shell scripts
├── src                       <- Source code
│   ├── data                     <- Dataset and datamodule
│   ├── model                    <- Model and Lightning module
│   ├── plugins                  <- Checkpoint plugin
│   ├── utils                    <- Trainer, metrics, and logger helpers
│   │   ├── checkpoint.py           <- Checkpoint path resolution
│   │   ├── logger.py               <- Logger construction and tip filter
│   │   ├── metrics.py              <- Per-split metric collections
│   │   └── trainer.py              <- Accelerator and callback helpers
│   ├── eval.py                  <- Run evaluation
│   └── train.py                 <- Run training
├── tests                     <- Tests
├── weights                   <- Local model weights
├── .env.example              <- Example environment variables
├── .gitignore                <- Files ignored by git
├── AGENTS.md                 <- Link to `.agents/AGENTS.md`
├── Dockerfile                <- Container image
├── LICENSE                   <- License
├── pixi.lock                 <- Locked Pixi environment
├── prek.toml                 <- prek hooks
├── pyproject.toml            <- Project metadata, Pixi, Ruff, and Pyrefly
└── README.md
```

## Organizing your research

You can use several checklists for your research, that are listed in the `docs/ai-ethics`:

- [REFORMS](https://reforms.cs.princeton.edu/)
- [The Open Ethics Canvas](https://openethics.ai/canvas/)
- [FAIR](https://guides.library.cmu.edu/researchdatamanagement/FAIR_principles)

## Cite

If you found this repo useful, you can cite it:

```bibtex
@software{iudin2026lightning_hydra,
  author       = {Iudin, Artyom},
  title        = {And another one lightning hydra template},
  year         = {2026},
  publisher    = {Zenodo},
  version      = {1.0.1},
  doi          = {10.5281/zenodo.24057788},
  url          = {https://doi.org/10.5281/zenodo.24057788}
}
```
