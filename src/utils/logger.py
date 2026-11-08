"""Logger construction and Lightning tip filtering."""

import logging

import hydra
from lightning.pytorch.loggers import Logger
from omegaconf import DictConfig


class _LightningTipFilter(logging.Filter):
    """Drop Lightning package-promotion tips."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Keep every record except a Lightning integration tip.

        Args:
            record (logging.LogRecord): Log record about to be emitted.

        Returns:
            ``False`` when the message is a package-promotion tip.

        """
        return "💡 Tip" not in record.getMessage()


def silence_lightning_tips() -> None:
    """Hide Lightning advertisements from the active loggers."""
    tip_filter = _LightningTipFilter()
    for handler in logging.getLogger().handlers:
        handler.addFilter(tip_filter)
    for name in (
        "lightning.pytorch.utilities.rank_zero",
        "pytorch_lightning.utilities.rank_zero",
    ):
        logging.getLogger(name).addFilter(tip_filter)


def get_loggers(cfg: DictConfig) -> list[Logger]:
    """Instantiate loggers in a Hydra config group.

    Args:
        cfg (DictConfig): Logger group. ``default`` holds shared settings. Each other entry is one logger.

    Returns:
        Instantiated loggers, excluding the ``default`` node.

    """
    return [hydra.utils.instantiate(cfg[name]) for name in cfg if name != "default"]
