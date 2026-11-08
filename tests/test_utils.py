"""Tests for trainer, metric, and logger helpers."""

import logging
from pathlib import Path

import pytest
import torch
from lightning.pytorch.callbacks import ModelCheckpoint
from lightning.pytorch.loggers import CSVLogger
from omegaconf import OmegaConf

from utils import (
    get_accelerator_devices_strategy,
    get_callbacks,
    get_loggers,
    get_metrics,
    resolve_ckpt_path,
    silence_lightning_tips,
)
from utils.trainer import _in_notebook


def test_resolve_ckpt_path_is_empty_when_unset(tmp_path: Path) -> None:
    """Training starts fresh when no checkpoint is configured."""
    assert resolve_ckpt_path(None, tmp_path) is None
    assert resolve_ckpt_path("", tmp_path) is None


def test_resolve_ckpt_path_rejects_a_non_string(tmp_path: Path) -> None:
    """A checkpoint path has to be a string."""
    with pytest.raises(TypeError, match="ckpt_path"):
        resolve_ckpt_path(3, tmp_path)


def test_resolve_ckpt_path_uses_the_launch_directory(tmp_path: Path) -> None:
    """A relative checkpoint path is resolved from the launch directory."""
    resolved = resolve_ckpt_path("runs/epoch=0-step=8", tmp_path)
    assert resolved == tmp_path / "runs/epoch=0-step=8"


def test_get_metrics_builds_an_independent_collection_per_split() -> None:
    """Each requested split gets its own copy of every metric."""
    metrics = get_metrics(
        OmegaConf.create(
            {
                "default": {"splits": ["train", "val"]},
                "accuracy": {
                    "_target_": "torchmetrics.Accuracy",
                    "task": "multiclass",
                    "num_classes": 2,
                    "average": "macro",
                    "splits": "${default.splits}",
                },
            },
        ),
    )
    metrics["train"]["accuracy"].update(torch.tensor([0, 1]), torch.tensor([0, 1]))
    metrics["val"]["accuracy"].update(torch.tensor([0]), torch.tensor([1]))

    assert set(metrics) == {"train", "val"}
    assert metrics["train"]["accuracy"] is not metrics["val"]["accuracy"]
    assert float(metrics["train"]["accuracy"].compute()) == 1.0
    assert float(metrics["val"]["accuracy"].compute()) == 0.0


def test_get_callbacks_skips_the_shared_default_node() -> None:
    """The ``default`` node is shared config, not a callback."""
    callbacks = get_callbacks(
        OmegaConf.create(
            {
                "default": {"metric": "val_f1"},
                "checkpointer": {"_target_": "lightning.pytorch.callbacks.ModelCheckpoint", "monitor": "val_f1"},
            },
        ),
    )
    assert len(callbacks) == 1
    assert isinstance(callbacks[0], ModelCheckpoint)
    assert callbacks[0].monitor == "val_f1"


def test_get_loggers_skips_the_shared_default_node(tmp_path: Path) -> None:
    """The ``default`` node is shared config, not a logger."""
    loggers = get_loggers(
        OmegaConf.create(
            {
                "default": {"name": "ignored"},
                "csv": {
                    "_target_": "lightning.pytorch.loggers.csv_logs.CSVLogger",
                    "save_dir": str(tmp_path),
                    "name": "csv",
                },
            },
        ),
    )
    assert len(loggers) == 1
    assert isinstance(loggers[0], CSVLogger)


def test_accelerator_matches_the_visible_devices() -> None:
    """The trainer target follows CUDA, and a single device stays on the auto strategy."""
    accelerator, devices, strategy = get_accelerator_devices_strategy()
    assert _in_notebook() is False
    if torch.cuda.is_available():
        assert accelerator == "gpu"
        assert devices == torch.cuda.device_count()
    else:
        assert accelerator == "cpu"
        assert devices == 1
    assert strategy == "auto" if devices == 1 else strategy == "ddp"


def test_silence_lightning_tips_drops_only_the_promotion() -> None:
    """Package-promotion messages are filtered and ordinary records remain."""
    logger = logging.getLogger("lightning.pytorch.utilities.rank_zero")
    records: list[logging.LogRecord] = []

    class _ListHandler(logging.Handler):
        """Collect records that pass the logger filters."""

        def emit(self, record: logging.LogRecord) -> None:
            """Store one accepted record.

            Args:
                record (logging.LogRecord): Record that reached this handler.

            """
            records.append(record)

    handler = _ListHandler()
    previous_level = logger.level
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    try:
        silence_lightning_tips()
        logger.info("💡 Tip: install an extra logger")
        logger.info("epoch finished")
    finally:
        logger.removeHandler(handler)
        logger.setLevel(previous_level)

    assert [record.getMessage() for record in records] == ["epoch finished"]
