"""Tests for split checkpoint reading and writing."""

import json
from pathlib import Path

import pytest
import torch

from plugins.split_checkpoint import SplitCheckpointIO


def test_save_and_load_roundtrip_splits_the_checkpoint(tmp_path: Path) -> None:
    """A ``.ckpt`` path becomes a directory of weights, metadata, and training state."""
    checkpoint_path = tmp_path / "epoch=0-step=8.ckpt"
    state_dict = {"weight": torch.tensor([1.0, 2.0])}
    SplitCheckpointIO().save_checkpoint(
        {"state_dict": state_dict, "epoch": 3, "global_step": 8, "loops": {"fit": "done"}},
        checkpoint_path,
    )

    loaded = SplitCheckpointIO().load_checkpoint(checkpoint_path)
    config = json.loads((tmp_path / "epoch=0-step=8" / "config.json").read_text(encoding="utf-8"))

    assert not checkpoint_path.exists()
    assert (tmp_path / "epoch=0-step=8" / "model.safetensors").is_file()
    assert (tmp_path / "epoch=0-step=8" / "training_states.pth").is_file()
    assert config["epoch"] == 3
    assert torch.equal(loaded["state_dict"]["weight"], state_dict["weight"])
    assert loaded["epoch"] == 3
    assert loaded["loops"] == {"fit": "done"}
    assert loaded["state_dict"]["weight"].device.type == "cpu"


def test_torch_weights_roundtrip_when_safetensors_is_off(tmp_path: Path) -> None:
    """``use_safetensors=False`` stores the state dict in ``model.pth``."""
    checkpoint_path = tmp_path / "weights"
    state_dict = {"weight": torch.ones(2, 2)}
    SplitCheckpointIO(use_safetensors=False).save_checkpoint({"state_dict": state_dict}, checkpoint_path)

    loaded = SplitCheckpointIO(use_safetensors=False).load_checkpoint(checkpoint_path, weights_only=True)
    assert (checkpoint_path / "model.pth").is_file()
    assert not (checkpoint_path / "model.safetensors").exists()
    assert torch.equal(loaded["state_dict"]["weight"], state_dict["weight"])


def test_remove_checkpoint_deletes_the_directory(tmp_path: Path) -> None:
    """Removing a checkpoint deletes the split directory and ignores a missing one."""
    checkpoint_path = tmp_path / "epoch=0-step=8.ckpt"
    plugin = SplitCheckpointIO()
    plugin.save_checkpoint({"state_dict": {"weight": torch.zeros(1)}}, checkpoint_path)
    plugin.remove_checkpoint(checkpoint_path)
    plugin.remove_checkpoint(checkpoint_path)
    assert not (tmp_path / "epoch=0-step=8").exists()


def test_save_rejects_storage_options_and_non_tensors(tmp_path: Path) -> None:
    """Cloud storage options and non-tensor weights are rejected."""
    plugin = SplitCheckpointIO()
    with pytest.raises(TypeError, match="storage_options"):
        plugin.save_checkpoint(
            {"state_dict": {"weight": torch.zeros(1)}},
            tmp_path / "checkpoint.ckpt",
            storage_options={},
        )
    with pytest.raises(TypeError, match="not a tensor"):
        plugin.save_checkpoint({"state_dict": {"weight": 1}}, tmp_path / "checkpoint.ckpt")


def test_load_requires_a_directory_and_a_weight_file(tmp_path: Path) -> None:
    """Loading fails when the directory or the weight file is missing."""
    with pytest.raises(FileNotFoundError, match="directory"):
        SplitCheckpointIO().load_checkpoint(tmp_path / "missing.ckpt")
    (tmp_path / "empty").mkdir()
    with pytest.raises(FileNotFoundError, match="weights"):
        SplitCheckpointIO().load_checkpoint(tmp_path / "empty")
