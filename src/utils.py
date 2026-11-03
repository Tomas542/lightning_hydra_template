"""Helpers for the trainer, metrics, and loggers."""

import logging
import sys
from typing import Any, Literal, cast

import hydra
import torch
from lightning.pytorch.callbacks import Callback
from lightning.pytorch.loggers import Logger
from omegaconf import DictConfig, OmegaConf
from torchmetrics import Metric, MetricCollection


class _LightningTipFilter(logging.Filter):
    """Drop Lightning package-promotion tips."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Keep every record except a Lightning integration tip.

        Args:
            record (logging.LogRecord): Log record about to be emitted.

        Returns:
            ``False`` when the message is a package-promotion tip.

        """
        return "💡 Tip" not in record.getMessage()


def silence_lightning_tips() -> None:
    """Hide Lightning advertisements from the active loggers."""
    tip_filter = _LightningTipFilter()
    for handler in logging.getLogger().handlers:
        handler.addFilter(tip_filter)
    for name in (
        "lightning.pytorch.utilities.rank_zero",
        "pytorch_lightning.utilities.rank_zero",
    ):
        logging.getLogger(name).addFilter(tip_filter)


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


def get_metrics(cfg: DictConfig) -> dict[str, MetricCollection]:
    """Build a separate metric collection for each split.

    Args:
        cfg (DictConfig): Metric group. ``default`` holds shared settings. Each other entry is one metric and names its
            splits.

    Returns:
        Split name to a collection of freshly instantiated metrics.

    """
    grouped: dict[str, dict[str, Metric | MetricCollection]] = {}
    for name, metric_cfg in cfg.items():
        if name == "default":
            continue
        raw = cast("dict[str, Any]", OmegaConf.to_container(metric_cfg, resolve=True))
        splits = cast("list[str]", raw.pop("splits"))
        for split in splits:
            grouped.setdefault(split, {})[str(name)] = cast("Metric", hydra.utils.instantiate(raw))
    return {split: MetricCollection(metrics) for split, metrics in grouped.items()}


def get_loggers(cfg: DictConfig) -> list[Logger]:
    """Instantiate loggers in a Hydra config group.

    Args:
        cfg (DictConfig): Logger group. ``default`` holds shared settings. Each other entry is one logger.

    Returns:
        Instantiated loggers, excluding the ``default`` node.

    """
    return [hydra.utils.instantiate(cfg[name]) for name in cfg if name != "default"]
