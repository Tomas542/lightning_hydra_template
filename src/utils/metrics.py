"""Per-split metric collections."""

from typing import Any, cast

import hydra
from omegaconf import DictConfig, OmegaConf
from torchmetrics import Metric, MetricCollection


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
