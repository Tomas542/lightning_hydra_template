"""Example of lightning module with hydra and other stuff"""

import hydra
import lighting.pytorch as L
import torchmetrics
from omegaconf import DictConfig
from torch import Tensor, nn, optim


class MyLightningModule(L.LightningModule):
    """Aswesome lightning module.

    Args:
        cfg (DictConfig): OmegaConf config.

    Attributes:
        train_metrics (MetricCollection): Classification metrics.
        cfg (DictConfig): Saved config.
        model (Module): Torch model.
        criterion (Module): Loss function.

    """

    def __init__(self, cfg: DictConfig) -> None:
        super().__init__()
        self.train_metrics = torchmetrics.MetricCollection(
            {
                "Accuracy": torchmetrics.Accuracy("multiclass", num_classes=self.cfg.num_classes),
                "Precision": torchmetrics.Precision("multiclass", num_classes=self.cfg.num_classes),
                "Recall": torchmetrics.Recall("multiclass", num_classes=self.cfg.num_classes),
                "F1": torchmetrics.F1Score("multiclass", num_classes=self.cfg.num_classes),
            },
            prefix="train_",
        )
        self.cfg = cfg
        self.model: nn.Module = hydra.utils.instantiate(self.cfg.model)
        self.criterion: nn.Module = hydra.utils.instantiate(self.cfg.criterion)

    def forward(self, features: Tensor) -> Tensor:
        return self.model(features)

    def _shared_step(self, batch: tuple) -> tuple[Tensor, Tensor]:
        features, labels = batch
        preds = self(features)
        return preds, labels

    def train_step(self, batch: tuple, _: int = 0) -> Tensor:
        preds, labels = self.__shared_step(batch)
        self.train_metrics(preds, labels)
        return self.criterion(preds, labels)

    def validation_step(self, batch: tuple, _: int = 0) -> Tensor:
        preds, labels = self.__shared_step(batch)
        return self.criterion(preds, labels)

    def test_step(self, batch: tuple, _: int = 0) -> Tensor:
        preds, labels = self.__shared_step(batch)
        return self.criterion(preds, labels)

    def configure_optimizer(self) -> optim.AdamW:
        return optim.AdamW(self.model.parameters(), lr=self.cfg.optimizer.lr)
