# Use case for lightning_hydra template

To use this repository as your template, use the GitHub UI and create your own repo from this template,
or clone it as a regular repository.

Then you can create virtual environment with `pixi` as:

```shell
pixi install
```

and then install additional packages you need with:

```shell
# Conda package
pixi add package_name

# PyPI package
pixi add package_name --pypi
```

If you need other versions of the base packages, edit `pyproject.toml`.
Use `dependencies` for PyPI packages and `tool.pixi.dependencies` for Conda packages.
Conda channels go in `tool.pixi`.

Additionally, `pixi` provides environments, so you can use it to separate development deps from base one.
In this template `prek` package for running pre-commit hooks is already placed as dev dependency.
To use it you can run:

```shell
# Installs dev dependencies
pixi install -e dev

# Installs hooks for Git
pixi run -e dev prek install
```

`pixi` stores a shared dependency once, so it is not copied into every environment.
`.pixi/environments/dev` then contains prek and its own dependencies.
Python and the other packages stay in `.pixi/environments/default`.

## Current configuration

All checks for code are currently configured the way:

```md
If this rule is presented in ruff - ruff will check it, instead of _tool_name_
```

Like `PyGrep` hooks checks only thing that `ruff` with `PGH` can't.

(WIP) The same rule implies in case of code checkers the way `ruff > pyrefly > ty` based on feature richness.

## How to improve

There are several steps you can do to improve overall code quality:

- Remove exceptions in `tool.ruff.lint` section;

- Increase docstring coverage of code in `tool.interrogate` section;

- Add tests with `unittest` or `pytest` and remove the `PY005` rule from `tool.repo-review`.
- If you choose `pytest`, add the `PT` rules in `tool.ruff.lint` and remove the `PP301` exception in `tool.repo-review`.

- If you use `async` or `FastAPI`, you can add it's rules either;

- Remove rules for `NumPy` or `Pandas` if you don't use them;

- Add `beartype` runtime type checking. Additionally you can add `jaxtyping` to enhance it with shape checking;

- Some type checkers can provide additional code checks, that you'd like to apply;

- Replace PyPI packages with Conda. This is the most opinionated change: Conda also ships system dependencies,
  so the environment is more platform agnostic.
  PyPI, on the other hand, lets you run the project with other tools, such as `uv` or `poetry`.

For more information about the last one, you can read on [pixi site](https://pixi.prefix.dev/latest/switching_from/uv/#why-the-conda-ecosystem-matters).

Even more opinionated step: use `Pydantic` to verify you configs.
You can define all your schemas from `configs` in, for example, `src/schemas`.
Then at the beginning of the main function validate your config with schemas and only after pass them into your model.

Pros:

- Pydantic validation is relatively cheap.
  Much cheaper, than wait for you models to load just to find out, that you made a mistake in one trainer argument.
- You can move `src/utils.py` logic inside this schemas.

Cons:

- It could be tricky, especially with `_target_` field in config,
- Adding doctrings with `typing.Annotated` and `typing.Doc` (python>=3.13) is also could be tricky with `Field`,
- `Pydantic` isn't that popular in research field, and benefits are negligible.
