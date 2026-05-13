"""Torch model code."""

from torch import Tensor, nn


class MyModel(nn.Module):
    """Model that do nothing."""

    def __init__(self) -> None:
        super().__init__()

    def forward(self, features: Tensor) -> Tensor:
        """Identity forward.

        Args:
            feature (Tensor): Some tensor.

        Returns:
            Tensor: same as feature.

        """
        return features
