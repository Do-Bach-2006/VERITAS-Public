# Baseline Detectors Framework

Welcome to the **Baseline Detectors Framework**! This is a comprehensive, modular malware detection suite designed for researchers and security practitioners. It provides a robust architecture for training, evaluating, predicting, and testing evasion robustness against various malware detection models.

## Overview
This standalone package encapsulates all essential model architectures, a dynamic execution controller (`main.py`), and a FastAPI server (`server.py`). It is built to seamlessly transition between single-model evaluations and complex ensemble-based predictions.

### Key Features
- **Unified Interface:** All models implement the `MalwareModelBase` class, ensuring consistent `.train()`, `.predict()`, `.evaluate()`, and `.evade()` methods.
- **Ensemble Support:** Easily combine multiple models with custom weights to build powerful ensemble detectors.
- **Smart Resource Management:** Automatically detects available hardware (GPU/CUDA, TPU/XLA, MPS, or CPU) and allocates system resources efficiently to prevent OOM errors.
- **Evasion Testing:** Native support for evaluating model robustness against adversarial samples and evasion techniques.

## Supported Models (9 Target Detector Configurations)
This framework includes the nine learning-based detector configurations (3 binary and 6 multiclass) evaluated in the paper:

1. **Binary MalConv (`binary_malconv`)**: Raw-byte CNN architecture for binary malware detection (2 MB window).
2. **Multiclass MalConv (`malconv`)**: Raw-byte CNN architecture with DeCov regularization for multiclass family classification (2 MB window).
3. **SeqConvAttn (`seqconvattn`)**: Raw-byte convolutional and 3-layer Transformer self-attention network (400 KB window).
4. **IMCFN (`imcfn`)**: Image-based VGG-16 fine-tuned convolutional network over $224 \times 224 \times 3$ jet-colormapped byte visualizations.
5. **MultiView CNN (`multiview_cnn`)**: Binary multi-view feature fusion 1D-CNN combining PE headers, opcodes, APIs, and bytes (2,128-d fused vector).
6. **Binary M-Attn-Health (`m_attn_health`)**: Binary 5-branch multi-view attention network over static PE, dynamic API, and image views.
7. **Multiclass M-Attn-Health (`m_attn_health_multi`)**: Multiclass 5-branch multi-view attention network (also used as an independent architecture for the local surrogate).
8. **RTF-CANINE (`rtf_cannie`)**: Ensemble of 10 character-level CANINE-S Transformer classifiers (max 2,048 characters).
9. **RTF-BERT (`rtf_bert`)**: Ensemble of 6 tokenized BERT Transformer classifiers (max 512 tokens).

## Quickstart

### Prerequisites
Make sure you have the required dependencies installed (primarily `torch`, `scikit-learn`, `matplotlib`, `seaborn`, `pandas`, `psutil`, `fastapi`, and `uvicorn`). 

### Running the Controller
The primary entry point is `main.py`, which is driven entirely by JSON configuration files.

```bash
# Run a specific task using a config file
python -m baseline_detectors.main --config config.json
```

For more details on how to write these configurations and use the framework, please refer to the following documentation files:

- [HOW_TO_USE.md](./HOW_TO_USE.md): Instructions on running predictions, evaluations, and evasion testing.
- [TRAINING_AND_TUNING.md](./TRAINING_AND_TUNING.md): Guide on training new models and dataset formats.
- [ARCHITECTURE.md](./ARCHITECTURE.md): Deep dive into the framework's core design and how to add new models.
