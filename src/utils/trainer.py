"""Accelerator selection and callback construction."""

import sys
from typing import Literal

import hydra
import torch
from lightning.pytorch.callbacks import Callback
from omegaconf import DictConfig


def _in_notebook() -> bool:
    """Return whether this process is a Jupyter kernel.

    IPython is not imported. A notebook kernel has already loaded it and registered ``IPKernelApp``.

    Returns:
        ``True`` when the active IPython shell is a notebook kernel.

    """
    ipython = sys.modules.get("IPython")
    if ipython is None:
        return False
    get_ipython = getattr(ipython, "get_ipython", None)
    if not callable(get_ipython):
        return False
    shell = get_ipython()
    config = getattr(shell, "config", None)
    return config is not None and "IPKernelApp" in config


def get_accelerator_devices_strategy() -> tuple[Literal["cpu", "gpu"], int, Literal["auto", "ddp", "ddp_notebook"]]:
    """Get the accelerator, devices, and strategy for the trainer."""
    accelerator = "gpu" if torch.cuda.is_available() else "cpu"
    devices = torch.cuda.device_count() or 1
    in_notebook = _in_notebook()
    strategy = "ddp_notebook" if in_notebook and devices > 1 else "ddp" if devices > 1 else "auto"

    return accelerator, devices, strategy


def get_callbacks(cfg: DictConfig) -> list[Callback]:
    """Instantiate callbacks in a Hydra config group.

    Args:
        cfg (DictConfig): Callback group. ``default`` holds shared settings. Each other entry is one callback.

    Returns:
        Instantiated callbacks, excluding the ``default`` node.

    """
    return [hydra.utils.instantiate(cfg[callback_name]) for callback_name in cfg if callback_name != "default"]
