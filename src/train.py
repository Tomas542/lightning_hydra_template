"""Train the dummy linear classifier."""

import logging

import hydra
import lightning.pytorch as L
from omegaconf import DictConfig

from utils import get_callbacks, get_metrics, silence_lightning_tips

log = logging.getLogger(__name__)


@hydra.main(version_base="1.3", config_path="../configs", config_name="main.yaml")
def main(cfg: DictConfig) -> None:
    """Fit the model and run the test loop.

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

    trainer.fit(model=lightning_module, datamodule=datamodule)
    trainer.test(model=lightning_module, datamodule=datamodule)


if __name__ == "__main__":
    main()
