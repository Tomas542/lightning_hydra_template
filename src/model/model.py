"""Torch model code."""

from typing import cast

from torch import Tensor, nn


class DummyModel(nn.Module):
    """Linear classifier.

    Args:
        in_features (int): Feature vector length.
        num_classes (int): Number of class logits.

    """

    def __init__(self, in_features: int, num_classes: int) -> None:
        super().__init__()
        self.linear = nn.Linear(in_features, num_classes)

    def forward(self, features: Tensor) -> Tensor:
        """Map features to class logits.

        Args:
            features (Tensor): Batch of feature vectors shaped ``(batch, in_features)``.

        Returns:
            Class logits shaped ``(batch, num_classes)``.

        """
        return cast("Tensor", self.linear(features))
