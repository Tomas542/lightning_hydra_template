import logging

import hydra
import lightning.pytorch as L
from omegaconf import DictConfig

from src.data import MyDataModule
from src.model import MyLightningModule
from utils import get_callbacks

log = logging.getLogger(__name__)


@hydra.main(version_base="1.3", config_path="./configs", config_name="main.yaml")
def main(cfg: DictConfig) -> None:
    if cfg.get("seed"):
        L.seed_everything(cfg.seed)
    logger = hydra.utils.instantiate(cfg.logger)
    callbacks = get_callbacks(cfg.callbacks)
    lm = MyLightningModule(cfg.lightning_module)
    dm = MyDataModule(cfg.datamodule)
    trainer: L.Trainer = hydra.utils.instantiate(cfg.trainer, logger=logger, callbacks=callbacks)

    trainer.fit(model=lm, datamodule=dm)
    trainer.test(model=lm, datamodule=dm)


if __name__ == "__main__":
    main()
