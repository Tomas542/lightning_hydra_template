"""Datasets and the Lightning datamodule."""

from .datamodule import DummyDataModule
from .dataset import DummyDataset

__all__ = ["DummyDataModule", "DummyDataset"]
