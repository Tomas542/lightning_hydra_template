"""Lightning module for the dummy linear classifier."""

import logging
from typing import Any, cast

import hydra
import lightning.pytorch as L
import torchmetrics
from lightning.pytorch.utilities.types import OptimizerLRScheduler
from omegaconf import DictConfig
from torch import Tensor, nn, optim

log = logging.getLogger(__name__)


class DummyLightningModule(L.LightningModule):
    """Linear classifier trained with cross-entropy and a warmup-cosine schedule.

    Args:
        model (DictConfig): Model config node. Instantiated inside this module.
        criterion (DictConfig): Loss config node. Instantiated inside this module.
        optimizer (DictConfig): Optimizer config node. Instantiated in ``configure_optimizers``.
        scheduler (DictConfig): Scheduler hyperparameters.
        metrics (dict[str, torchmetrics.MetricCollection]): Metric collections keyed by split name:
            ``train``, ``val``, and ``test``.

    """

    def __init__(
        self,
        model: DictConfig,
        criterion: DictConfig,
        optimizer: DictConfig,
        scheduler: DictConfig,
        metrics: dict[str, torchmetrics.MetricCollection],
    ) -> None:
        super().__init__()
        self.model = cast("nn.Module", hydra.utils.instantiate(model))
        self.criterion = cast("nn.Module", hydra.utils.instantiate(criterion))
        self.optimizer_cfg = optimizer
        self.scheduler_cfg = scheduler
        self.metrics = dict(metrics)
        for split, collection in self.metrics.items():
            self.add_module(f"{split}_metrics", collection)

    def forward(self, features: Tensor) -> Tensor:
        """Delegate to the wrapped model.

        Args:
            features (Tensor): Batch of feature vectors.

        Returns:
            Class logits.

        """
        return cast("Tensor", self.model(features))

    def _shared_step(self, batch: tuple[Tensor, Tensor]) -> tuple[Tensor, Tensor]:
        """Run the model on one batch.

        Args:
            batch (tuple[Tensor, Tensor]): Features and class labels.

        Returns:
            Logits and labels.

        """
        features, labels = batch
        return self(features), labels

    def _log_split(
        self,
        split: str,
        metrics: torchmetrics.MetricCollection,
        loss: Tensor,
        preds: Tensor,
        labels: Tensor,
    ) -> None:
        """Log loss and classification metrics for one split.

        Args:
            split (str): Split name used as the metric prefix.
            metrics (torchmetrics.MetricCollection): Metric collection updated with this batch.
            loss (Tensor): Batch loss.
            preds (Tensor): Class logits.
            labels (Tensor): Class indices.

        """
        metrics.update(preds, labels)
        batch_size = labels.shape[0]
        self.log(f"{split}_loss", loss, on_step=False, on_epoch=True, prog_bar=True, batch_size=batch_size)
        for name, metric in metrics.items():
            self.log(
                f"{split}_{name}",
                metric,
                on_step=False,
                on_epoch=True,
                prog_bar=name == "f1",
                batch_size=batch_size,
            )

    def training_step(self, batch: tuple[Tensor, Tensor], _batch_idx: int) -> Tensor:
        """Compute the training loss and update train metrics.

        Args:
            batch (tuple[Tensor, Tensor]): Features and class labels.
            _batch_idx (int): Index of the batch in the epoch.

        Returns:
            Cross-entropy loss.

        """
        preds, labels = self._shared_step(batch)
        loss = cast("Tensor", self.criterion(preds, labels))
        self._log_split("train", self.metrics["train"], loss, preds, labels)
        return loss

    def validation_step(
        self,
        batch: tuple[Tensor, Tensor],
        _batch_idx: int,
    ) -> Tensor:
        """Compute the validation loss and update validation metrics.

        Args:
            batch (tuple[Tensor, Tensor]): Features and class labels.
            _batch_idx (int): Index of the batch in the epoch.

        Returns:
            Cross-entropy loss.

        """
        preds, labels = self._shared_step(batch)
        loss = cast("Tensor", self.criterion(preds, labels))
        self._log_split("val", self.metrics["val"], loss, preds, labels)
        return loss

    def test_step(self, batch: tuple[Tensor, Tensor], _batch_idx: int) -> Tensor:
        """Compute the test loss and update test metrics.

        Args:
            batch (tuple[Tensor, Tensor]): Features and class labels.
            _batch_idx (int): Index of the batch in the epoch.

        Returns:
            Cross-entropy loss.

        """
        preds, labels = self._shared_step(batch)
        loss = cast("Tensor", self.criterion(preds, labels))
        self._log_split("test", self.metrics["test"], loss, preds, labels)
        return loss

    def configure_optimizers(self) -> OptimizerLRScheduler:
        """Create optimizer and the warmup-then-cosine schedule.

        Returns:
            Adam and a scheduler config. ``interval`` comes from the scheduler config.

        """
        optimizer = cast("optim.Optimizer", hydra.utils.instantiate(self.optimizer_cfg, params=self.parameters()))
        scheduler = self._init_scheduler(optimizer)
        interval = str(self.scheduler_cfg.interval)
        return cast(
            "OptimizerLRScheduler",
            ([optimizer], [{"scheduler": scheduler, "interval": interval}]),
        )

    def _init_scheduler(self, optimizer: optim.Optimizer) -> optim.lr_scheduler.SequentialLR:
        """Build a linear warmup followed by cosine decay.

        The optimizer's base learning rate is the warmup peak. The schedule length is the number of optimizer steps in
        the fit: training-set length divided by the batch size, then multiplied by ``max_epochs``.

        Args:
            optimizer (optim.Optimizer): Optimizer whose learning rate is scheduled.

        Returns:
            Sequential schedule that warms up, then follows cosine annealing.

        """
        min_lr = float(self.scheduler_cfg.min_lr)
        max_lr = float(self.scheduler_cfg.max_lr)
        warmup_steps = int(self.scheduler_cfg.warmup_steps)
        total_steps = self._optimizer_steps()
        warmup_scheduler = optim.lr_scheduler.LinearLR(
            optimizer,
            start_factor=min_lr / max_lr,
            end_factor=1.0,
            total_iters=warmup_steps,
        )
        cosine_scheduler = optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=total_steps - warmup_steps,
            eta_min=min_lr,
        )
        return optim.lr_scheduler.SequentialLR(
            optimizer,
            schedulers=[warmup_scheduler, cosine_scheduler],
            milestones=[warmup_steps],
        )

    def _optimizer_steps(self) -> int:
        """Count optimizer steps from the training set, batch size, and ``max_epochs``.

        The training loader drops a partial last batch, so one epoch is ``len(train_dataset) // batch_size``.

        Returns:
            Optimizer steps the warmup-cosine schedule should cover.

        Raises:
            RuntimeError: The trainer has no datamodule.
            TypeError: The datamodule does not expose ``train_dataset`` and a positive ``batch_size``.
            ValueError: Those values cannot produce a schedule longer than the warmup.

        """
        # Assigned on the trainer instance by Lightning's data connector, not declared on the class.
        datamodule = cast("Any", self.trainer).datamodule
        if datamodule is None:
            message = "A datamodule is required to size the learning-rate schedule."
            raise RuntimeError(message)
        train_dataset = getattr(datamodule, "train_dataset", None)
        batch_size = getattr(datamodule, "batch_size", None)
        if train_dataset is None or not isinstance(batch_size, int) or batch_size < 1:
            message = "The datamodule must provide train_dataset and a positive batch_size."
            raise TypeError(message)
        steps_per_epoch = len(train_dataset) // batch_size
        epochs = self.trainer.max_epochs
        if steps_per_epoch < 1 or not isinstance(epochs, int) or epochs < 1:
            message = "The training set, batch size, and max_epochs must yield at least one optimizer step per epoch."
            raise ValueError(message)
        total_steps = steps_per_epoch * epochs
        warmup_steps = int(self.scheduler_cfg.warmup_steps)
        if warmup_steps >= total_steps:
            message = "warmup_steps must be shorter than the optimizer steps derived from the training set."
            raise ValueError(message)
        log.info(
            "Scheduler total_steps=%s (samples=%s, batch_size=%s, epochs=%s)",
            total_steps,
            len(train_dataset),
            batch_size,
            epochs,
        )
        return total_steps
