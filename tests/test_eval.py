"""Tests for loading checkpoint weights and writing test metrics."""

import json
from pathlib import Path

import torch
from omegaconf import OmegaConf
from torch import nn

from eval import load_weights, save_test_metrics
from model.lightning_model import DummyLightningModule
from plugins.split_checkpoint import SplitCheckpointIO


def _module() -> DummyLightningModule:
    """Build a small classifier with no logged metrics.

    Returns:
        Untrained Lightning module.

    """
    return DummyLightningModule(
        model=OmegaConf.create({"_target_": "model.model.DummyModel", "in_features": 4, "num_classes": 2}),
        criterion=OmegaConf.create({"_target_": "torch.nn.CrossEntropyLoss"}),
        optimizer=OmegaConf.create({}),
        scheduler=OmegaConf.create({}),
        metrics={},
    )


def test_load_weights_restores_the_saved_state_dict(tmp_path: Path) -> None:
    """Weights written by the split checkpoint plugin replace the module parameters."""
    source = _module()
    linear = source.get_submodule("model.linear")
    assert isinstance(linear, nn.Linear)
    with torch.no_grad():
        linear.weight.fill_(1.0)
    checkpoint = tmp_path / "epoch=0-step=8.ckpt"
    SplitCheckpointIO().save_checkpoint({"state_dict": source.state_dict()}, checkpoint)

    restored = _module()
    load_weights(restored, SplitCheckpointIO(), checkpoint)
    restored_linear = restored.get_submodule("model.linear")
    assert isinstance(restored_linear, nn.Linear)
    assert torch.equal(restored_linear.weight, linear.weight)


def test_save_test_metrics_writes_json_in_the_checkpoint_directory(tmp_path: Path) -> None:
    """Test metrics are stored inside the checkpoint directory, not beside the ``.ckpt`` name."""
    checkpoint = tmp_path / "epoch=0-step=8.ckpt"
    SplitCheckpointIO().save_checkpoint({"state_dict": _module().state_dict()}, checkpoint)

    written = save_test_metrics(checkpoint, [{"test_loss": torch.tensor(0.5), "test_f1": torch.tensor(0.25)}])
    payload = json.loads(written.read_text(encoding="utf-8"))

    assert written == tmp_path / "epoch=0-step=8" / "test_metrics.json"
    assert payload == {"test_loss": 0.5, "test_f1": 0.25}
