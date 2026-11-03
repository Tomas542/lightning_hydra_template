"""Train the dummy linear classifier."""

import logging
from pathlib import Path

import hydra
import lightning.pytorch as L
from omegaconf import DictConfig

from utils import get_callbacks, get_metrics, resolve_ckpt_path, silence_lightning_tips

log = logging.getLogger(__name__)


@hydra.main(version_base="1.3", config_path="../configs", config_name="main.yaml")
def main(cfg: DictConfig) -> None:
    """Fit the model and run the test loop.

    A set ``ckpt_path`` resumes training from that split checkpoint. Weights, optimizer state, and epoch progress are
    restored. ``max_epochs`` still comes from this run's config.

    Args:
        cfg (DictConfig): Composed Hydra configuration.

    """
    silence_lightning_tips()
    if cfg.get("seed"):
        L.seed_everything(cfg.seed)
        log.info("Seed set to %s", cfg.seed)

    logger = hydra.utils.instantiate(cfg.logger)
    callbacks = get_callbacks(cfg.callbacks)
    metrics = get_metrics(cfg.metrics)
    lightning_module = hydra.utils.instantiate(cfg.lightning_module, metrics=metrics)
    datamodule = hydra.utils.instantiate(cfg.datamodule)
    trainer: L.Trainer = hydra.utils.instantiate(cfg.trainer, logger=logger, callbacks=callbacks)
    ckpt_path = resolve_ckpt_path(cfg.get("ckpt_path"), Path(hydra.utils.get_original_cwd()))
    if ckpt_path is None:
        log.info("Starting from randomly initialized weights")
    else:
        log.info("Resuming from %s", ckpt_path)

    trainer.fit(model=lightning_module, datamodule=datamodule, ckpt_path=ckpt_path)
    trainer.test(model=lightning_module, datamodule=datamodule)


if __name__ == "__main__":
    main()
