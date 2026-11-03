"""Tests for the dummy dataset and datamodule."""

import numpy as np
import torch
from torch.utils.data import RandomSampler, SequentialSampler

from data.datamodule import DummyDataModule
from data.dataset import DummyDataset


def test_dataset_returns_features_and_in_range_labels() -> None:
    """Each sample is one feature vector and a label inside the class range."""
    state = np.random.get_state()
    np.random.seed(0)
    try:
        dataset = DummyDataset(count=32, in_features=4, num_classes=2)
        features, label = dataset[0]
        own_class_feature = dataset.data[np.arange(len(dataset)), dataset.labels]
    finally:
        np.random.set_state(state)

    assert len(dataset) == 32
    assert features.shape == (4,)
    assert features.dtype == np.float32
    assert 0 <= int(label) < 2
    assert own_class_feature.mean() > 0.5


def test_datamodule_drops_only_the_partial_training_batch() -> None:
    """Training drops the partial batch. Validation and test keep it."""
    datamodule = DummyDataModule(
        batch_size=8,
        num_workers=0,
        pin_memory=False,
        train_samples=20,
        val_samples=10,
        test_samples=6,
        in_features=4,
        num_classes=2,
    )
    datamodule.setup("fit")
    datamodule.setup("test")
    train_loader = datamodule.train_dataloader()
    val_loader = datamodule.val_dataloader()
    test_loader = datamodule.test_dataloader()

    assert len(datamodule.train_dataset) == 20
    assert len(datamodule.val_dataset) == 10
    assert len(datamodule.test_dataset) == 6
    assert train_loader.drop_last is True
    assert len(train_loader) == 2
    assert isinstance(train_loader.sampler, RandomSampler)
    assert val_loader.drop_last is False
    assert len(val_loader) == 2
    assert isinstance(val_loader.sampler, SequentialSampler)
    assert len(test_loader) == 1


def test_datamodule_pins_memory_only_when_cuda_can_use_it() -> None:
    """Pinned memory follows the config on CUDA and stays off without it."""
    datamodule = DummyDataModule(
        batch_size=4,
        num_workers=0,
        pin_memory=True,
        train_samples=4,
        val_samples=4,
        test_samples=4,
        in_features=4,
        num_classes=2,
    )
    assert datamodule.pin_memory is torch.cuda.is_available()
