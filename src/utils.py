from typing import Literal

import hydra
import torch
from lightning.pytorch.callbacks import Callback
from lightning.pytorch.loggers import Logger
from omegaconf import DictConfig
from torchmetrics import Metric


def get_accelerator_devices_strategy() -> tuple[Literal["cpu", "gpu"], int, Literal["auto", "ddp", "ddp_notebook"]]:
    accelerator = "gpu" if torch.cuda.is_available() else "cpu"
    devices = torch.cuda.device_count() or 1

    try:
        import IPython

        in_notebook = "IPKernelApp" in IPython.get_ipython().config

    except ImportError:
        in_notebook = False

    strategy = "ddp_notebook" if in_notebook and devices > 1 else "ddp" if devices > 1 else "auto"

    return accelerator, devices, strategy


def get_callbacks(cfg: DictConfig) -> list[Callback]:
    """Parses callbacks from config"""
    return [hydra.utils.instantiate(cfg[callback_name]) for callback_name in cfg if callback_name != "default"]


def get_metrics(cfg: DictConfig) -> list[Metric]:
    """Parses torchmetrics from config"""
    return [hydra.utils.instantiate(cfg[callback_name]) for callback_name in cfg if callback_name != "default"]


def get_loggers(cfg: DictConfig) -> list[Logger]:
    """Parses loggers from config"""
    loggers = []
    for callback_name in cfg:
        if callback_name != "default":
            # monkey patch
            if callback_name == "trackio":
                import sys
                import trackio as wandb

                sys.modules["wandb"] = wandb

            loggers.append(hydra.utils.instantiate(cfg[callback_name]))
    return loggers
