"""Checkpoint IO that stores weights separately from training state."""

import io
import json
import logging
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any, cast

import torch
from lightning.fabric.plugins.io.torch_io import TorchCheckpointIO
from safetensors.torch import load_file, save_file
from torch import Tensor

log = logging.getLogger(__name__)

_CONFIG_KEYS = frozenset(
    {
        "epoch",
        "global_step",
        "pytorch-lightning_version",
        "hyper_parameters",
        "CHECKPOINT_HYPER_PARAMS_NAME",
        "CHECKPOINT_HYPER_PARAMS_KEY",
        "CHECKPOINT_HYPER_PARAMS_TYPE",
    },
)


def _default_map_location(storage: Any, _location: Any) -> Any:
    """Keep a stored tensor where it was loaded."""
    return storage


def _atomic_torch_save(checkpoint: dict[str, Any], path: Path) -> None:
    """Write a PyTorch checkpoint by replacing a temporary file.

    Args:
        checkpoint (dict[str, Any]): Object accepted by ``torch.save``.
        path (Path): Destination file.

    """
    buffer = io.BytesIO()
    torch.save(checkpoint, buffer)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_bytes(buffer.getvalue())
    temporary.replace(path)


def _torch_load(path: Path, map_location: Any, weights_only: bool | None) -> dict[str, Any]:
    """Load a PyTorch checkpoint dictionary.

    Args:
        path (Path): File written by ``_atomic_torch_save``.
        map_location (Any): ``torch.load`` storage remapping.
        weights_only (bool | None): Forwarded to ``torch.load``.

    Returns:
        The dictionary stored in the file.

    Raises:
        TypeError: The file does not contain a dictionary.

    """
    loaded = torch.load(path, map_location=map_location, weights_only=weights_only)
    if not isinstance(loaded, dict):
        message = "Checkpoint file does not contain a dictionary."
        raise TypeError(message)
    return cast("dict[str, Any]", loaded)


def _save_safetensors(weights: dict[str, Tensor], path: Path) -> None:
    """Write tensors with ``safetensors.torch.save_file``.

    Args:
        weights (dict[str, Tensor]): Contiguous CPU tensors.
        path (Path): Destination ``.safetensors`` file.

    """
    save_file(weights, path)


def _load_safetensors(path: Path) -> dict[str, Tensor]:
    """Read tensors with ``safetensors.torch.load_file``.

    Args:
        path (Path): ``.safetensors`` file.

    Returns:
        Tensors loaded on CPU.

    """
    return load_file(path, device="cpu")


def _checkpoint_dir(path: str | Path) -> Path:
    """Return the directory used for one split checkpoint.

    Args:
        path (str | Path): Checkpoint path. A ``.ckpt`` suffix is removed so Lightning's filename becomes the directory
            name.

    Returns:
        Directory that holds the weight file, config, and training state.

    """
    checkpoint_dir = Path(str(path))
    if checkpoint_dir.suffix == ".ckpt":
        return checkpoint_dir.with_suffix("")
    return checkpoint_dir


def _json_ready(config: dict[str, Any]) -> dict[str, Any]:
    """Convert checkpoint metadata into values ``json`` can encode.

    Args:
        config (dict[str, Any]): Metadata copied out of the Lightning checkpoint.

    Returns:
        The same mapping, with non-JSON values replaced by their string form.

    """
    ready: dict[str, Any] = {}
    for key, value in config.items():
        try:
            json.dumps(value)
        except (TypeError, ValueError):
            ready[key] = str(value)
        else:
            ready[key] = value
    return ready


def _weight_tensors(state_dict: dict[str, Any]) -> dict[str, Tensor]:
    """Copy state-dict tensors onto CPU for safetensors.

    Args:
        state_dict (dict[str, Any]): Model ``state_dict`` from the Lightning checkpoint.

    Returns:
        Contiguous CPU tensors keyed by parameter name.

    Raises:
        TypeError: A state-dict entry is not a tensor.

    """
    weights: dict[str, Tensor] = {}
    for key, value in state_dict.items():
        if not isinstance(value, Tensor):
            message = f"State dict entry {key} is not a tensor."
            raise TypeError(message)
        weights[key] = value.detach().cpu().contiguous()
    return weights


def _place_weights(weights: dict[str, Tensor], map_location: Any) -> dict[str, Tensor]:
    """Move loaded weights according to Lightning's ``map_location``.

    Args:
        weights (dict[str, Tensor]): Tensors loaded from safetensors.
        map_location (Any): Callable, device, or ``None``.

    Returns:
        Weights after ``map_location`` is applied.

    """
    if map_location is None:
        return weights
    if callable(map_location):
        return {key: map_location(value, None) for key, value in weights.items()}
    return {key: value.to(map_location) for key, value in weights.items()}


class SplitCheckpointIO(TorchCheckpointIO):
    """Save model weights apart from optimizer and trainer state.

    The checkpoint path Lightning passes in, without a ``.ckpt`` suffix, becomes a directory:

    ```
    checkpoint_name/
    ├── config.json
    ├── model.safetensors
    └── training_states.pth
    ```

    Args:
        use_safetensors (bool): Write ``model.safetensors`` when true, otherwise ``model.pth``.

    """

    def __init__(self, use_safetensors: bool = True) -> None:
        super().__init__()
        self.use_safetensors = use_safetensors

    def save_checkpoint(
        self,
        checkpoint: dict[str, Any],
        path: str | Path,
        storage_options: Any | None = None,
    ) -> None:
        """Save weights, metadata, and training state as separate files.

        Args:
            checkpoint (dict[str, Any]): Lightning checkpoint dictionary.
            path (str | Path): Target path. A ``.ckpt`` suffix selects the directory name.
            storage_options (Any | None): Unused. Lightning cloud storage options are not supported.

        Raises:
            TypeError: ``storage_options`` was provided.

        """
        if storage_options is not None:
            message = "storage_options is not supported by SplitCheckpointIO."
            raise TypeError(message)

        checkpoint_dir = _checkpoint_dir(path)
        checkpoint_dir.mkdir(parents=True, exist_ok=True)

        model_data: dict[str, Any] = {}
        training_data: dict[str, Any] = {}
        config_data: dict[str, Any] = {}
        for key, value in checkpoint.items():
            if key == "state_dict":
                model_data[key] = value
            elif key in _CONFIG_KEYS:
                config_data[key] = value
            else:
                training_data[key] = value

        if self.use_safetensors and "state_dict" in model_data:
            _save_safetensors(_weight_tensors(model_data["state_dict"]), checkpoint_dir / "model.safetensors")
        else:
            _atomic_torch_save(model_data, checkpoint_dir / "model.pth")

        config_path = checkpoint_dir / "config.json"
        config_path.write_text(json.dumps(_json_ready(config_data), indent=2), encoding="utf-8")

        if training_data:
            _atomic_torch_save(training_data, checkpoint_dir / "training_states.pth")
        log.debug("Saved split checkpoint to %s", checkpoint_dir)

    def load_checkpoint(
        self,
        path: str | Path,
        map_location: Callable[..., Any] | None = _default_map_location,
        weights_only: bool | None = None,
    ) -> dict[str, Any]:
        """Load a split checkpoint back into one Lightning dictionary.

        Args:
            path (str | Path): Checkpoint directory, or the ``.ckpt`` path Lightning stored.
            map_location (Callable[..., Any] | None): Remaps tensors from ``model.pth`` and ``training_states.pth``.
                Safetensors are loaded on CPU and then passed through this callable or moved to this device.
            weights_only (bool | None): Forwarded to ``torch.load`` for the ``.pth`` files.

        Returns:
            Checkpoint dictionary with ``state_dict`` and training state combined.

        Raises:
            FileNotFoundError: The directory or the weight file is missing.

        """
        checkpoint_dir = _checkpoint_dir(path)
        if not checkpoint_dir.is_dir():
            message = f"Checkpoint directory not found: {checkpoint_dir}"
            raise FileNotFoundError(message)

        checkpoint: dict[str, Any] = {}
        config_path = checkpoint_dir / "config.json"
        if config_path.is_file():
            checkpoint.update(json.loads(config_path.read_text(encoding="utf-8")))

        safetensors_path = checkpoint_dir / "model.safetensors"
        torch_path = checkpoint_dir / "model.pth"
        if safetensors_path.is_file():
            checkpoint["state_dict"] = _place_weights(_load_safetensors(safetensors_path), map_location)
        elif torch_path.is_file():
            checkpoint.update(_torch_load(torch_path, map_location, weights_only))
        else:
            message = f"Model weights file not found in {checkpoint_dir}"
            raise FileNotFoundError(message)

        training_path = checkpoint_dir / "training_states.pth"
        if training_path.is_file():
            checkpoint.update(_torch_load(training_path, map_location, weights_only))
        return checkpoint

    def remove_checkpoint(self, path: str | Path) -> None:
        """Remove the split checkpoint directory.

        Args:
            path (str | Path): Checkpoint directory, or the ``.ckpt`` path Lightning stored.

        """
        checkpoint_dir = _checkpoint_dir(path)
        if checkpoint_dir.is_dir():
            shutil.rmtree(checkpoint_dir)
            log.debug("Removed checkpoint directory %s", checkpoint_dir)
