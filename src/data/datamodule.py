"""Lightning datamodule for the dummy classification example."""

from enum import Enum

import lightning.pytorch as L
import numpy as np
import torch
from torch.utils.data import DataLoader

from .dataset import DummyDataset


class TaskType(Enum):
    """Split whose dataloader is being built."""

    TRAIN = "train"
    VAL = "val"
    TEST = "test"


class DummyDataModule(L.LightningDataModule):
    """In-memory classification datamodule.

    Args:
        batch_size (int): Size of one batch.
        num_workers (int): Number of parallel loader processes.
        pin_memory (bool): Copy tensors into pinned memory when CUDA is available.
        train_samples (int): Number of training samples.
        val_samples (int): Number of validation samples.
        test_samples (int): Number of test samples.
        in_features (int): Feature vector length.
        num_classes (int): Number of class labels.

    """

    def __init__(
        self,
        batch_size: int,
        num_workers: int,
        *,
        pin_memory: bool,
        train_samples: int,
        val_samples: int,
        test_samples: int,
        in_features: int,
        num_classes: int,
    ) -> None:
        super().__init__()
        # Data loading parameters
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory if torch.cuda.is_available() else False

        # Dataset parameters
        self.train_samples = train_samples
        self.val_samples = val_samples
        self.test_samples = test_samples

        # Model parameters
        self.in_features = in_features
        self.num_classes = num_classes

        # Datasets
        self.train_dataset: DummyDataset
        self.val_dataset: DummyDataset
        self.test_dataset: DummyDataset

    def setup(self, stage: str) -> None:
        """Create the datasets for the requested stage.

        Args:
            stage (str): Lightning stage name, ``fit`` or ``test``.

        """
        match stage:
            case "fit":
                self.train_dataset = DummyDataset(self.train_samples, self.in_features, self.num_classes)
                self.val_dataset = DummyDataset(self.val_samples, self.in_features, self.num_classes)
            case "test":
                self.test_dataset = DummyDataset(self.test_samples, self.in_features, self.num_classes)

    def _get_dataloader(
        self,
        dataset: DummyDataset,
        task_type: TaskType,
    ) -> DataLoader[tuple[np.ndarray, np.int64]]:
        """Build a dataloader for one split.

        Args:
            dataset (DummyDataset): Dataset for this split.
            task_type (TaskType): Split that controls shuffling and dropping the last batch.

        Returns:
            Dataloader over ``dataset``.

        """
        return DataLoader(
            dataset,
            batch_size=self.batch_size,
            pin_memory=self.pin_memory,
            num_workers=self.num_workers,
            shuffle=task_type == TaskType.TRAIN,
            drop_last=task_type == TaskType.TRAIN,
        )

    def train_dataloader(self) -> DataLoader[tuple[np.ndarray, np.int64]]:
        """Return the training dataloader."""
        return self._get_dataloader(self.train_dataset, TaskType.TRAIN)

    def val_dataloader(self) -> DataLoader[tuple[np.ndarray, np.int64]]:
        """Return the validation dataloader."""
        return self._get_dataloader(self.val_dataset, TaskType.VAL)

    def test_dataloader(self) -> DataLoader[tuple[np.ndarray, np.int64]]:
        """Return the test dataloader."""
        return self._get_dataloader(self.test_dataset, TaskType.TEST)
