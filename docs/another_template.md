# Why another Lightning-Hydra template

There are already several awesome repos, like:

- [ashleve/lightning-hydra-template](https://github.com/ashleve/lightning-hydra-template)
- [gorodnitskiy/yet-another-lightning-hydra-template](https://github.com/gorodnitskiy/yet-another-lightning-hydra-template)

It is important to note that they are more mature in terms of development.
This template aims at agentic development and a more modern Python ecosystem.

## Versions

| Piece       | ashleve    | gorodnitskiy | this repo |
| ----------- | ---------- | ------------ | --------- |
| Python      | 3.8–3.10   | unpinned     | 3.12 only |
| Torch       | 2.0+       | 1.10+        | 2.7.1     |
| Lightning   | 2.0+       | 1.8.3        | 2.6.0     |
| Hydra       | 1.3.2      | 1.3.1        | 1.3.7+    |
| Environment | conda, pip | pip, Docker  | pixi      |

## Differences

- Ecosystem: this repo uses `pixi` and `prek`. The other templates use `pre-commit` and `pip/conda`.
  Code checks like `ruff` and the other hooks come to more than 20.
- Safety: a package cooldown limits supply-chain exposure, along with model scanning,
  virtual-environment scanning, and safetensors checkpoints.
  `ruff`'s bandit rules are basic checks, not a guarantee.
- CI is GitHub Actions on the free `ubuntu-latest` runner. It runs `prek` and `zizmor`. Dependabot groups action updates.
- Neither original has an agentic copilot layout.
  This repo has `.agents/`: `AGENTS.md` and skills for experiment launch, code review, refactor, and research notes.
  It also has skills for paper drafting, documentation, checklists, commits, and security.

## Safety

This template provides several layers of checks:

- `ruff`'s bandit rules
- `grype` scans of installed environments
- package cooldown
- weight pickle scanners `picklescan`, `modelaudit`, and `fickling`

These fall into code safety and model-loading safety.

### Code safety

When you add dependencies, check them for known vulnerabilities.
Pixi supports a package cooldown, which refuses packages published after the configured date.
That limits exposure to a fresh supply-chain attack.

The template also offers `grype` scanning for vulnerabilities, following
[this proposal](https://github.com/scientific-python/upload-nightly-action/pull/164).
Scan the environments after Pixi installs them, and before you run training or evaluation.

```shell
pixi run -e safe scan_envs
```

`scan_envs` inspects environments that Pixi has already installed.
Pixi installs `dependencies` before that task runs, so this scan does not replace the cooldown.

The last code check is `ruff` with bandit rules.
It scans code for some unsafe practices, and it implements only some of the bandit rules.
For a broader scan, install the `bandit` package itself.

### Model loading safety

Model scanning is organized as a `pixi` task and can be launched as:

```shell
pixi run -e safe scan_model /path/to/model
```

Though this command doesn't use `fickling` scanning, since its tracing is hard to read. You can run it as follows:

```shell
pixi run -e safe fickling --trace /path/to/model
```

#### Scanners showed nothing. Am I okay?

There could be false negatives. Scanners are not ideal. If `scan_model` reports nothing suspicious at all and traces are ok, you are probably fine.

#### Scanners showed a warning. How bad is this?

There could also be false positives.
From an overview of the scanners, `modelaudit` is the most accurate if you want to rely on one scanner only.
If some of the scanners show warnings or other stuff, check the traces.
