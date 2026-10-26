---
name: refactor
description: 'Surgical code refactoring to improve maintainability without changing behavior in ML research codebases. Covers cleaning training loops, modularizing model architectures, improving tensor type safety, eliminating code smells, and optimizing PyTorch pipelines.'
license: MIT
---

# Refactor

## Overview

Improve machine learning code structure, readability, and reproducibility without altering model outputs or training dynamics. Refactoring in ML research means transitioning messy experimental scripts into clean, modular, and maintainable pipelines.

## When to Use
Use this skill when:

- Training scripts (`train.py`), data pipelines, or model definitions (`src/models/`) become bloated or hard to debug.
- Code smells make it difficult to introduce new loss functions, augmentations, or architectures.
- User asks to clean up model code, modularize training loops, or improve type annotations in research code.

## Refactoring Principles for ML Research

### The Golden Rules

1. Numerical Equivalence is Preserved - Refactoring must not alter forward/backward passes, random seeding, or metric outcomes unless explicitly intended.
2. Small Steps & Smoke Tests - Make tiny changes and run quick smoke tests (src/train.py trainer.fast_dev_run=True) or unit tests (pytest) after each step.
3. Version Control - Commit before and after each safe state.
4. Isolate Randomness - Ensure seeding (torch.manual_seed, np.random.seed) remains intact across refactored utility modules.

### Common Code Smells & Fixes in ML Research

1. Monolithic Training Step / Long Function

```diff
# BAD: 150-line training loop handling data loading, forward pass, loss, backward, clipping, and logging all at once
- def train_epoch(model, dataloader, optimizer, device):
-     model.train()
-     for batch in dataloader:
-         # 30 lines of data unpacking & device movement
-         # 20 lines of forward pass & loss computation
-         # 30 lines of gradient accumulation & clipping
-         # 40 lines of metric logging and wandb tracking
-         pass

# GOOD: Broken into focused, single-responsibility helper functions
+ def train_epoch(model: nn.Module, dataloader: DataLoader, optimizer: Optimizer, device: torch.device) -> float:
+     model.train()
+     total_loss = 0.0
+     for batch in dataloader:
+         inputs, targets = move_batch_to_device(batch, device)
+         loss = compute_forward_and_loss(model, inputs, targets)
+         optimizer.zero_grad()
+         loss.backward()
+         clip_and_step_optimizer(model, optimizer)
+         total_loss += loss.item()
+     return total_loss / len(dataloader)
```

2. Duplicated Data Preprocessing

```diff
# BAD: Repeating feature extraction or normalization logic across train, val, and test data loaders
- def process_train_audio(audio_path):
-     waveform, sr = librosa.load(audio_path, sr=16000)
-     waveform = waveform / np.max(np.abs(waveform))
-     return librosa.feature.melspectrogram(y=waveform, sr=sr)
-
- def process_val_audio(audio_path):
-     waveform, sr = librosa.load(audio_path, sr=16000)
-     waveform = waveform / np.max(np.abs(waveform))
-     return librosa.feature.melspectrogram(y=waveform, sr=sr)

# GOOD: Extract common transformation pipeline
+ def load_and_extract_mel(audio_path: str, target_sr: int = 16000) -> np.ndarray:
+     waveform, sr = librosa.load(audio_path, sr=target_sr)
+     normalized_wav = waveform / (np.max(np.abs(waveform)) + 1e-8)
+     return librosa.feature.melspectrogram(y=normalized_wav, sr=target_sr)
```

3. God Trainer Class

```diff
# BAD: Massive Trainer class handling checkpointing, validation, wandb logging, distributed training, and dataset building
- class ExperimentManager:
-     def load_data(self): pass
-     def build_model(self): pass
-     def train(self): pass
-     def validate(self): pass
-     def save_checkpoint(self): pass
-     def upload_to_wandb(self): pass
-     # 40 more methods...

# GOOD: Delegation to modular services / PyTorch Lightning modules
+ class AudioModel(LightningModule):
+     def training_step(self, batch, batch_idx): ...
+     def validation_step(self, batch, batch_idx): ...
+
+ class CheckpointManager:
+     def save(self, state: dict, path: str) -> None: ...
```

4. Long Parameter Lists in Model Initializations

```diff
# BAD: Too many constructor arguments for model architecture
- def __init__(self, d_model, n_heads, n_layers, d_ff, dropout, activation, max_seq_len, vocab_size, pad_token_id):
-     pass

# GOOD: Group model hyperparameters into a configuration dataclass or Hydra config object
+ @dataclass
+ class TransformerConfig:
+     d_model: int = 768
+     n_heads: int = 12
+     n_layers: int = 12
+     dropout: float = 0.1
+     max_seq_len: int = 2048
+
+ def __init__(self, config: TransformerConfig) -> None:
+     super().__init__()
+     self.config = config
```

5. Feature Envy in Custom Metrics

```diff
# BAD: Metric calculation function reaches deep into model internals or optimizer states
- def compute_gradient_norm(model):
-     total_norm = 0.0
-     for p in model.transformer.encoder.layers.parameters():
-         param_norm = p.grad.data.norm(2)
-         total_norm += param_norm.item() ** 2
-     return total_norm ** 0.5

# GOOD: Encapsulate gradient inspection or keep logic inside model interface
+ class AudioClassifier(nn.Module):
+     def get_grad_norm(self) -> float:
+         return torch.nn.utils.clip_grad_norm_(self.parameters(), max_norm=float('inf'))
```

6. Primitive Obsession for Loss or Optimizers

```diff
# BAD: Using raw strings or magic numbers for loss selection
- if loss_type == "ce":
-     loss = F.cross_entropy(logits, targets)
- elif loss_type == "focal":
-     loss = focal_loss(logits, targets, alpha=0.25)

# GOOD: Use Enums or strategy classes
+ class LossType(StrEnum):
+     CROSS_ENTROPY = "cross_entropy"
+     FOCAL = "focal"
+     MSE = "mse"
+
+ def get_loss_fn(loss_type: LossType) -> nn.Module:
+     match loss_type:
+         case LossType.CROSS_ENTROPY:
+             return nn.CrossEntropyLoss()
+         case LossType.FOCAL:
+             return FocalLoss(alpha=0.25)
+         case _:
+             raise ValueError(f"Unsupported loss: {loss_type}")
```

7. Magic Numbers in Neural Networks

```diff
# BAD: Unexplained tensor shapes, epsilon values, or learning rates hardcoded in code
- x = x.view(-1, 8, 64)
- eps = 1e-8
- lr = 3e-4

# GOOD: Named constants with descriptive names or Hydra config bindings
+ NUM_ATTENTION_HEADS: Final[int] = 8
+ HEAD_DIMENSION: Final[int] = 64
+ EPSILON: Final[float] = 1e-8
+
+ x = x.view(-1, NUM_ATTENTION_HEADS, HEAD_DIMENSION)
```

8. Nested Conditionals in Data Validation or Masking

```diff
# BAD: Deeply nested checks for padding masks or sequence lengths
- def process_batch(batch):
-     if batch is not None:
-         if "audio" in batch:
-             if batch["audio"].dim() == 2:
-                 if batch["audio"].shape[0] > 0:
-                     return pad_sequence(batch["audio"])

# GOOD: Guard clauses / early returns
+ def process_batch(batch: dict[str, torch.Tensor] | None) -> torch.Tensor:
+     if batch is None or "audio" not in batch:
+         raise ValueError("Invalid batch structure")
+     audio = batch["audio"]
+     if audio.dim() != 2 or audio.shape[0] == 0:
+         raise ValueError(f"Unexpected audio tensor shape: {audio.shape}")
+     return pad_sequence(audio)
```

9. Dead Code in Research Iterations

```diff
# BAD: Leftover experimental code, unused model variants, or commented-out architectures
- # def old_attention_mechanism_v1(q, k, v):
- #     pass
- # UNUSED_GLOBAL_SCALE = 42.0

# GOOD: Delete unused functions and experimental code. Rely on Git history for past explorations.
```

10. Inappropriate Intimacy

```diff
# BAD: Training script reaches directly into tokenizer internal vocab files or dataset private attributes
- vocab_size = trainer.model.encoder.embeddings.word_embeddings.weight.shape[0]

# GOOD: Expose clean public properties on the model or config
+ vocab_size = model.get_vocab_size()
```

Extract Method Refactoring: Preprocessing Pipeline

```diff
# Before: One long dataset preparation function
- def prepare_dataset(raw_dir):
-     files = os.listdir(raw_dir)
-     processed = []
-     for f in files:
-         if f.endswith(".wav"):
-             path = os.path.join(raw_dir, f)
-             wav, sr = librosa.load(path, sr=16000)
-             if len(wav) < 16000:
-                 wav = np.pad(wav, (0, 16000 - len(wav)))
-             else:
-                 wav = wav[:16000]
-             mel = librosa.feature.melspectrogram(y=wav, sr=16000)
-             processed.append(mel)
-     return np.array(processed)

# After: Extracted modular functions
+ def prepare_dataset(raw_dir: str) -> np.ndarray:
+     wav_files = get_audio_filepaths(raw_dir)
+     processed_spectrograms = [process_single_audio(p) for p in wav_files]
+     return np.stack(processed_spectrograms)
+
+ def get_audio_filepaths(raw_dir: str) -> list[str]:
+     return [os.path.join(raw_dir, f) for f in os.listdir(raw_dir) if f.endswith(".wav")]
+
+ def process_single_audio(filepath: str, target_length: int = 16000) -> np.ndarray:
+     wav, sr = librosa.load(filepath, sr=16000)
+     padded_wav = pad_or_truncate_audio(wav, target_length)
+     return librosa.feature.melspectrogram(y=padded_wav, sr=16000)
+
+ def pad_or_truncate_audio(wav: np.ndarray, target_length: int) -> np.ndarray:
+     if len(wav) < target_length:
+         return np.pad(wav, (0, target_length - len(wav)))
+     return wav[:target_length]
```

Introducing Type Safety for PyTorch Tensors

```diff
# Before: Untyped functions accepting arbitrary dictionaries
- def compute_loss(model, batch):
-     logits = model(batch['input'])
-     return F.cross_entropy(logits, batch['target'])

# After: Fully typed function signatures with PyTorch tensors
+ import torch
+ from torch import Tensor
+
+ def compute_loss(model: nn.Module, batch: dict[str, Tensor]) -> Tensor:
+     inputs: Tensor = batch["input"]
+     targets: Tensor = batch["target"]
+     logits: Tensor = model(inputs)
+  
+     if logits.ndim != 2 or targets.ndim != 1:
+         raise RuntimeError(f"Unexpected tensor dimensions: logits {logits.shape}, targets {targets.shape}")
+  
+     return F.cross_entropy(logits, targets)
```

## Safe Refactoring Process for ML
1. PREPARE
  - Ensure existing smoke tests and unit tests pass (`pixi run -e test pytest`)
  - Commit current working state to Git
  - Create a dedicated refactoring branch

2. IDENTIFY
  - Isolate code smells in training loops, data loaders, or model modules
  - Verify expected input/output shapes and tensor types

3. REFACTOR (Small steps)
  - Apply one single transformation (e.g., extract method or introduce config dataclass)
  - Run a quick smoke test (`pixi run python src/train.py trainer.fast_dev_run=True`)
  - Commit passing changes

4. VERIFY
  - Ensure metric calculations and loss convergence remain identical
  - Run full test suite (`pixi run -e test pytest`)
  - Run lint checks (`pixi run -e dev format` / `pixi run -e dev check_fix`)

5. CLEAN UP
  - Update docstrings and type hints
  - Final commit


## Refactoring Checklist for ML Research

### Code Quality & Tensors

[ ] Functions and training steps are concise and single-purpose
[ ] Tensor shapes and data types are explicitly documented in type hints
[ ] No duplicated data augmentation or feature extraction logic
[ ] Magic numbers (learning rates, dimensions, epsilons) extracted to constants or Hydra configs
[ ] Dead code, commented-out architectures, and unused checkpoints removed

### Structure & Reproducibility

[ ] Code organized logically (`src/models/`, `src/data/`, `src/utils/`)
[ ] Random seed reproducibility verified across refactored modules
[ ] Configuration management handled cleanly via Hydra or dataclasses

### Testing & Verification

[ ] Refactored code passes smoke test (`trainer.fast_dev_run=True`)
[ ] Unit tests pass successfully (`pixi run -e test pytest`)
[ ] Linter checks pass without errors (`pixi run -e dev check_fix`)
