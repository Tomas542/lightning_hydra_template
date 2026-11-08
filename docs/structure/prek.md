# prek

Sections of `prek.toml`. `exclude` skips `.pixi/`, `.venv/`, and `.snap`. `default_stages` is `pre-commit`.
Each later block is one hook repository, and the comment above it is the section name.
The number in parentheses is that hook's `priority`.

## builtin

Checks that ship with prek:

- `detect-private-key` (0) looks for private keys.
- `check-added-large-files` (2) rejects large added files.
- `end-of-file-fixer` (10) and `trailing-whitespace` (20) fix file endings.
  The whitespace hook keeps Markdown line breaks (`--markdown-linebreak-ext=md`).
- `check-json` (30), `check-yaml` (50), and `check-toml` (50) parse those formats.

## git specific

`gitleaks` v8.30.1 (1) scans the commit for secrets.

## markdown

- `prettier` v3.9.10 (30) formats YAML and Markdown under `configs/`, `docs/`, `.github/`, and `.devcontainer/`, plus `README.md` and `.yamllint`.
- `markdownlint` v0.49.1 (40) lints Markdown. Settings are in `.markdownlint.yaml`.

## shell scripts

`shellcheck` v0.11.0.1 (30) checks `scripts/*.sh`.

## pyproject

- `pyproject-fmt` v2.30.1 (30) formats `pyproject.toml`. Arguments are `--no-print-diff` and `--keep-full-version`.
- `validate-pyproject` 0.26 (40) checks that file against its schemas. The extra dependency is `validate-pyproject-schema-store[all]`.

## yaml

`yamllint` v1.38.0 (40) lints `configs/` and `.yamllint`, using `.yamllint` and `--strict`.

## github actions

`zizmor` v1.26.1 (60) checks the workflows under `.github/workflows/`.

## python

- `nb-clean` v5.0.0 (30) cleans `notebook/`. It removes empty cells and keeps cell outputs.
- `interrogate` 1.7.0 (30) checks docstring coverage in `src/`. The threshold and ignored names are in `pyproject.toml`.
- `ruff-check` v0.17.0 (40) lints `src/`, `notebook/`, and `tests/` with `--fix`.
- `ruff-format` v0.17.0 (50) formats those trees plus `docs/` and `README.md`, including Markdown.
- `pyrefly-check` 1.3.2 (60) type-checks `src/`, `notebook/`, and `tests/`.
- `rst-backticks` (70) and `rst-directive-colons` (80), from pygrep-hooks v1.10.0, check `src/` and `tests/`.
  They stay because Ruff's `PGH` rules do not cover them.
- `sp-repo-review` from cookie `2026.08.14` (90) validates the repository. Its hook name in this file is `Validate Python repository`.
- `typos` v1.51.1 (100) spell-checks the tree.
