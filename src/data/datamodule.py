from enum import Enum

import lightning.pytorch as L
import torch
from torch.utils.data import DataLoader

from .dataset import MyDataset


class TaskType(Enum):
    TRAIN = "train"
    VAL = "val"
    TEST = "test"


class MyDataModule(L.LightningDataModule):
    """My awesome datamodule.

    Args:
        batch_size (int): Size of one batch.
        num_workers (int): Number of parallel processes.
        pin_memory (bool): Async data loading.

    Attributes:
        batch_size (int): Size of one batch.
        num_workers (int): Number of parallel processes.
        pin_memory (bool): Async data loading.


    """

    def __init__(
        self,
        batch_size: int,
        num_workers: int,
        pin_memory: bool,
    ) -> None:
        super().__init__()
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.pin_memory = pin_memory if torch.cuda.is_available() else False

    def setup(self, stage: str) -> None:
        match stage:
            case "fit":
                self.train_dataset = MyDataset()
                self.val_dataset = MyDataset()
            case "test":
                self.test_dataset = MyDataset()

    def __get_dataloader(self, dataset: MyDataset, task_type: TaskType) -> DataLoader:
        return DataLoader(
            dataset,
            batch_size=self.batch_size,
            pin_memory=self.pin_memory,
            num_workers=self.num_workers,
            shuffle=task_type == TaskType.TRAIN,
            drop_last=task_type == TaskType.TRAIN,
        )

    def train_dataloader(self) -> DataLoader:
        return self.__get_dataloader(self.train_dataset, TaskType.TRAIN)

    def val_dataloader(self) -> DataLoader:
        return self.__get_dataloader(self.val_dataset, TaskType.VAL)

    def test_dataloader(self) -> DataLoader:
        return self.__get_dataloader(self.test_dataset, TaskType.TEST)
