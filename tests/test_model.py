"""Tests for the linear model and its Lightning module."""

from types import SimpleNamespace
from typing import Any, cast

import pytest
import torch
from omegaconf import OmegaConf
from torch import Tensor, nn
from torchmetrics import Accuracy, MetricCollection

from data.datamodule import DummyDataModule
from model.lightning_model import DummyLightningModule
from model.model import DummyModel


def _ignore_log(*_args: object, **_kwargs: object) -> None:
    """Drop Lightning logging while a step is called outside a trainer."""


def _module() -> DummyLightningModule:
    """Build a small classifier with one accuracy metric per split.

    Returns:
        Lightning module whose schedule uses Adam and a one-step warmup.

    """
    metrics = {
        split: MetricCollection({"accuracy": Accuracy(task="multiclass", num_classes=2, average="macro")})
        for split in ("train", "val", "test")
    }
    return DummyLightningModule(
        model=OmegaConf.create({"_target_": "model.model.DummyModel", "in_features": 4, "num_classes": 2}),
        criterion=OmegaConf.create({"_target_": "torch.nn.CrossEntropyLoss"}),
        optimizer=OmegaConf.create({"_target_": "torch.optim.Adam", "lr": 1.0e-3}),
        scheduler=OmegaConf.create({"interval": "step", "min_lr": 1.0e-6, "max_lr": 1.0e-3, "warmup_steps": 4}),
        metrics=metrics,
    )


def _attach(module: DummyLightningModule, datamodule: object, max_epochs: int) -> None:
    """Point the module at the datamodule that sizes its schedule.

    Args:
        module (DummyLightningModule): Module under test.
        datamodule (object): Object with the attributes the schedule reads.
        max_epochs (int): Epoch count used to size the schedule.

    """
    module.trainer = SimpleNamespace(datamodule=datamodule, max_epochs=max_epochs)  # type: ignore[assignment]


def test_model_maps_a_batch_to_class_logits() -> None:
    """The linear layer returns one logit vector per sample."""
    logits = DummyModel(in_features=4, num_classes=3)(torch.zeros(5, 4))
    assert logits.shape == (5, 3)


@pytest.mark.parametrize(
    ("method_name", "split"),
    [("training_step", "train"), ("validation_step", "val"), ("test_step", "test")],
)
def test_split_step_returns_a_finite_loss(method_name: str, split: str) -> None:
    """Each split step returns a finite loss and updates that split's metric."""
    module = _module()
    module.log = _ignore_log
    features = torch.randn(4, 4)
    labels = torch.randint(0, 2, (4,))
    loss: Tensor = getattr(module, method_name)((features, labels), 0)
    accuracy = module.metrics[split]["accuracy"].compute()

    assert loss.ndim == 0
    assert torch.isfinite(loss)
    assert torch.isfinite(accuracy)


def test_configure_optimizers_accepts_a_schedule_longer_than_warmup() -> None:
    """Dropped partial batches still leave a schedule longer than the warmup."""
    module = _module()
    datamodule = DummyDataModule(
        batch_size=8,
        num_workers=0,
        pin_memory=False,
        train_samples=20,
        val_samples=4,
        test_samples=4,
        in_features=4,
        num_classes=2,
    )
    datamodule.setup("fit")
    _attach(module, datamodule, max_epochs=3)

    optimizers, schedulers = cast(
        "tuple[list[torch.optim.Optimizer], list[dict[str, Any]]]",
        module.configure_optimizers(),
    )
    assert isinstance(optimizers[0], torch.optim.Adam)
    assert schedulers[0]["interval"] == "step"
    assert isinstance(schedulers[0]["scheduler"], torch.optim.lr_scheduler.SequentialLR)


def test_configure_optimizers_rejects_a_warmup_that_covers_the_run() -> None:
    """The warmup cannot be as long as the optimizer steps derived from the data."""
    module = _module()
    datamodule = DummyDataModule(
        batch_size=8,
        num_workers=0,
        pin_memory=False,
        train_samples=20,
        val_samples=4,
        test_samples=4,
        in_features=4,
        num_classes=2,
    )
    datamodule.setup("fit")
    _attach(module, datamodule, max_epochs=1)
    with pytest.raises(ValueError, match="warmup_steps"):
        module.configure_optimizers()


def test_configure_optimizers_requires_a_training_dataset() -> None:
    """The schedule cannot be sized without the training set and batch size."""
    module = _module()
    _attach(module, SimpleNamespace(batch_size=8), max_epochs=1)
    with pytest.raises(TypeError, match="train_dataset"):
        module.configure_optimizers()


def test_forward_uses_the_wrapped_linear_layer() -> None:
    """The Lightning module returns the wrapped model's logits."""
    module = _module()
    linear = module.get_submodule("model.linear")
    assert isinstance(linear, nn.Linear)
    logits = module(torch.zeros(2, 4))
    assert logits.shape == (2, linear.out_features)
