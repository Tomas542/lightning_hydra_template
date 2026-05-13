"""Torch dataset codes"""

import numpy as np
from torch.utils.data import Dataset


class MyDataset(Dataset):
    def __init__(self, count: int = 10) -> None:
        self.count = count
        self.data = np.random.rand(
            count,
            16000,
        ).astype(np.float32)
        self.labels = np.random.randint(0, 2, size=count)

    def __len__(self) -> int:
        return self.count

    def __getitem__(self, idx: int) -> tuple:
        """Batch x Time"""
        return self.data[idx], self.labels[idx]
