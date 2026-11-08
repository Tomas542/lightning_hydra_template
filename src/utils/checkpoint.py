"""Checkpoint path resolution."""

from pathlib import Path
from typing import Any


def resolve_ckpt_path(ckpt_path: Any, original_cwd: Path) -> Path | None:
    """Resolve ``ckpt_path`` against the directory where the run was launched.

    Args:
        ckpt_path (Any): Value of ``ckpt_path`` from the composed config.
        original_cwd (Path): Working directory before Hydra changed it.

    Returns:
        Absolute checkpoint directory or ``.ckpt`` path, or ``None`` when no checkpoint was set.

    Raises:
        TypeError: ``ckpt_path`` is not a string.

    """
    if ckpt_path is None or ckpt_path == "":
        return None
    if not isinstance(ckpt_path, str):
        message = "ckpt_path must be a string path."
        raise TypeError(message)
    path = Path(ckpt_path)
    if not path.is_absolute():
        path = original_cwd / path
    return path
