"""Synthetic datasets for the dummy example."""

import numpy as np
from torch.utils.data import Dataset


class DummyDataset(Dataset[tuple[np.ndarray, np.int64]]):
    """Classification dataset generated in memory.

    Each class has its own mean, and samples are that mean plus a little noise.
    A linear layer can fit this.

    Args:
        count (int): Number of samples to generate.
        in_features (int): Length of each feature vector.
        num_classes (int): Number of class labels.

    """

    def __init__(self, count: int, in_features: int, num_classes: int) -> None:
        self.count = count
        self.labels = np.random.randint(0, num_classes, size=count, dtype=np.int64)
        means = np.eye(num_classes, in_features, dtype=np.float32)
        noise = np.random.randn(count, in_features).astype(np.float32)
        self.data = means[self.labels] + 0.1 * noise

    def __len__(self) -> int:
        return self.count

    def __getitem__(self, index: int) -> tuple[np.ndarray, np.int64]:
        """Return one feature vector and its class label.

        Args:
            index (int): Sample index.

        Returns:
            Feature vector of shape ``(in_features,)`` and an integer label.

        """
        return self.data[index], self.labels[index]
