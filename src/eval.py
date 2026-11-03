"""Evaluate a trained dummy classifier."""

import json
import logging
from collections.abc import Sequence
from pathlib import Path
from typing import Any, cast

import hydra
import lightning.pytorch as L
from omegaconf import DictConfig
from torch import Tensor

from plugins.split_checkpoint import SplitCheckpointIO, _checkpoint_dir
from utils import get_callbacks, get_metrics, resolve_ckpt_path, silence_lightning_tips

log = logging.getLogger(__name__)


def load_weights(module: L.LightningModule, checkpoint_io: SplitCheckpointIO, ckpt_path: Path) -> None:
    """Load the checkpoint ``state_dict`` into the Lightning module.

    Args:
        module (L.LightningModule): Module created from the current config.
        checkpoint_io (SplitCheckpointIO): Reader configured for split checkpoints.
        ckpt_path (Path): Checkpoint directory, or the ``.ckpt`` path Lightning recorded.

    Raises:
        TypeError: The checkpoint has no tensor ``state_dict``.

    """
    checkpoint = checkpoint_io.load_checkpoint(ckpt_path)
    state_dict = checkpoint.get("state_dict")
    if not isinstance(state_dict, dict) or not all(isinstance(value, Tensor) for value in state_dict.values()):
        message = "Checkpoint does not contain a tensor state_dict."
        raise TypeError(message)
    module.load_state_dict(cast("dict[str, Tensor]", state_dict))


def save_test_metrics(ckpt_path: Path, metrics: list[dict[str, Any]]) -> Path:
    """Write test metrics into the split checkpoint directory.

    One test dataloader is stored as a single object. Several dataloaders are stored as a list.

    Args:
        ckpt_path (Path): Checkpoint directory, or the ``.ckpt`` path Lightning recorded.
        metrics (list[dict[str, Any]]): Dictionaries returned by ``Trainer.test``.

    Returns:
        Path of the written ``test_metrics.json`` file.

    """
    payload: Any = metrics[0] if len(metrics) == 1 else metrics
    destination = _checkpoint_dir(ckpt_path) / "test_metrics.json"
    destination.write_text(json.dumps(_json_ready(payload), indent=2) + "\n", encoding="utf-8")
    return destination


def _json_ready(value: Any) -> Any:
    """Convert metric values into objects ``json`` can encode.

    Args:
        value (Any): Metric value, or a nested list or dictionary of them.

    Returns:
        JSON-compatible value.

    """
    if isinstance(value, Tensor):
        array = value.detach().cpu()
        return array.item() if array.ndim == 0 else array.tolist()
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, str | bytes):
        return [_json_ready(item) for item in value]
    if isinstance(value, float | int | str | bool) or value is None:
        return value
    return str(value)


@hydra.main(version_base="1.3", config_path="../configs", config_name="main.yaml")
def main(cfg: DictConfig) -> None:
    """Load a checkpoint, run the test loop, and store the metrics beside it.

    Args:
        cfg (DictConfig): Composed Hydra configuration.

    """
    silence_lightning_tips()
    if cfg.get("seed"):
        L.seed_everything(cfg.seed)
        log.info("Seed set to %s", cfg.seed)

    ckpt_path = resolve_ckpt_path(cfg.ckpt_path, Path(hydra.utils.get_original_cwd()))
    if ckpt_path is None:
        message = "Set ckpt_path to a split checkpoint before evaluation."
        raise ValueError(message)
    logger = hydra.utils.instantiate(cfg.logger)
    callbacks = get_callbacks(cfg.callbacks)
    metrics = get_metrics(cfg.metrics)
    lightning_module = hydra.utils.instantiate(cfg.lightning_module, metrics=metrics)
    checkpoint_io = cast("SplitCheckpointIO", hydra.utils.instantiate(cfg.checkpoint_io))
    load_weights(lightning_module, checkpoint_io, ckpt_path)
    datamodule = hydra.utils.instantiate(cfg.datamodule)
    trainer: L.Trainer = hydra.utils.instantiate(cfg.trainer, logger=logger, callbacks=callbacks)

    results = trainer.test(model=lightning_module, datamodule=datamodule)
    metrics_path = save_test_metrics(ckpt_path, cast("list[dict[str, Any]]", results))
    log.info("Saved test metrics to %s", metrics_path)


if __name__ == "__main__":
    main()
