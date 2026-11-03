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

## Organizing your research

You can use several checklists for your research, that are listed in the `docs/ai-ethics`:

- [REFORMS](https://reforms.cs.princeton.edu/)
- [The Open Ethics Canvas](https://openethics.ai/canvas/)
- [FAIR](https://guides.library.cmu.edu/researchdatamanagement/FAIR_principles)
