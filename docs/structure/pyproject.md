# pyproject

Sections of `pyproject.toml`, in file order.
`scripts/setup.sh` fills the author and, when `origin` is set, the `Source` URL.
It does not change the other sections.

## build-system

Hatchling builds the package.

## project

The distribution name is `my-project`, version `0.1`. Python is `>=3.12,<3.13`.
Runtime dependencies are `hydra-core`, `lightning==2.6.0`, `python-dotenv`, `safetensors`,
and the Torch 2.7.1 stack: `torch`, `torchaudio`, `torchvision`, and `torchmetrics`.

## project.urls

`Source` starts as `https://github.com/user/project`.

## dependency-groups

These groups are Pixi features. They are not installed with the default environment.

- `dev` has `prek`, `pyrefly`, and `ruff`.
- `test` has `pytest`, `pytest-cov`, and `pytest-xdist`.
- `extend` has `beartype`, `codecarbon`, `jaxtyping`, and `pydantic`.
- `notebook` has `ipykernel` and `ipywidgets`.
- `safe` has `fickling`, `modelaudit`, and `picklescan`.

## tool.pixi.workspace

Channels are `conda-forge` and the prefix-labs channel. The platform is `linux-64`. Pixi must be `>=0.82.1`.
`exclude-newer` is `2026-10-12`, so a package published after that date is not taken.

## tool.pixi.pypi-dependencies

`torch`, `torchaudio`, and `torchvision` are installed from the PyTorch CUDA 12.6 wheel index. The versions match the `[project]` pins.

## tool.pixi.feature.dev.tasks

Each task takes one `path`.

- `fix` runs `ruff check {{path}} --fix`.
- `check_fix` runs that, then `pyrefly check {{path}}`.
- `format` runs the Ruff fix, then `ruff format {{path}}`.

## tool.pixi.feature.safe.dependencies

The Conda package `grype` is added to the `safe` feature.

## tool.pixi.feature.safe.tasks

- `scan_model` runs `picklescan` and then `modelaudit` on one path.
- `scan_envs` runs `grype` on `.pixi/envs`.
- `scan_env` runs `grype` on one environment name.

## tool.pixi.feature.test.tasks

`cov` runs `pytest --cov-report=term-missing tests/`. The measured package is set in `tool.coverage.run`.

## tool.pixi.environments

`default`, `dev`, `notebook`, `safe`, `extend`, and `test`.
Every environment uses the solve group `default`, so they share one lock.
`dev`, `notebook`, `safe`, `extend`, and `test` each turn on the feature of the same name.

## tool.ruff

The line length is 120.

## tool.ruff.format

Indent is spaces, quotes are double, and the magic trailing comma is kept. Code samples inside docstrings are formatted, at length 80.

## tool.ruff.lint.extend-per-file-ignores

Notebooks ignore `T201`, so a `print` in a cell is allowed.

## tool.ruff.lint

`select` enables the families named in the file, from builtin shadowing (`A`) through flake8-2020 (`YTT`).
`DOC` is selected and does nothing until Ruff preview is on.

`ignore` turns off a fixed list: unannotated `*args` and `**kwargs`, `Any`, a docstring on `__init__` (`D107`),
two docstring layout rules (`D203`, `D213`), ambiguous names, non-lowercase arguments, NumPy's random module,
`try` inside a loop, imports that are not at module top level, the `PLR09` count rules, magic-number comparisons,
assign-before-return, asserts, and a required author or link on `TODO`.

`task-tags` is `TODO`.

## tool.repo-review

`PP004` is ignored because the Python upper bound is intentional.
`PY006` is ignored because hooks live in `prek.toml` instead of `.pre-commit-config.yaml`.

## tool.interrogate

Docstring coverage must stay at or above 40%. The style is Google.
Init modules, dunder methods, private and semiprivate names, properties, modules,
nested functions and classes, and overloaded functions are ignored.
The ignore regex also skips dataloader helpers, `*_step`, `configure_optimizers`, `forward`, `prepare`, and `setup`.

## tool.pyproject-fmt

Width is 120 and indent is 4. Python version classifiers are not generated. `max_supported_python` is `3.13`.
Tables use the long format, and `project.authors` stays collapsed.

## tool.pyrefly

The check targets Python 3.12 on Linux. The interpreter is `.pixi/envs/default/bin/python3`.
Included trees are `notebook`, `src`, and `tests`. The search path is `src`.
Site packages are the `default`, `notebook`, and `test` environments.
Unannotated definitions are checked. The minimum severity is `error`, and the preset is `strict`.

## tool.pyrefly.errors

`no-any-return`, `unannotated-return`, `unused-type-ignore`, and `unused-coroutine` are errors.
`redundant-cast`, `pytorch-efficiency-lints`, and `bad-unpacking` warn.
`missing-override-decorator` and `bad-override` are ignored.
Lightning hook stubs are typed as `*args` and `**kwargs`, so `@override` does not match them.

## tool.pytest

`addopts` is `-ra`. Warnings are errors. The log level is `INFO`. Pytest must be at least 9.
`pythonpath` is `src`, config and markers are strict, and the tests are in `tests/`.

## tool.coverage.run

Coverage is collected from `src`.
