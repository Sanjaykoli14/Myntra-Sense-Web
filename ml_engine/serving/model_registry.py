"""
Model Registry & Quantization Configurations for Myntra Sense AI Engine.
Tracks model versions, execution backends, and INT8/FP16 quantization specs.
"""

from typing import Dict, Any


MODEL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "two_tower_intent_v1": {
        "framework": "PyTorch / ONNX Runtime",
        "precision": "INT8_QUANTIZED",
        "input_dim": 64,
        "p95_latency_budget_ms": 5.0,
        "max_batch_size": 128,
        "description": "User and Item semantic vector embedding models"
    },
    "gbdt_conversion_propensity_v1": {
        "framework": "Treelite / LightGBM C++",
        "precision": "FP16",
        "p95_latency_budget_ms": 3.0,
        "max_batch_size": 256,
        "description": "30-day conversion propensity ranker"
    },
    "bayesian_sizing_v1": {
        "framework": "C++ / TorchScript",
        "precision": "FP32",
        "p95_latency_budget_ms": 2.0,
        "max_batch_size": 64,
        "description": "Bayesian collaborative sizing matcher"
    },
    "roberta_absa_v1": {
        "framework": "TensorRT / Triton",
        "precision": "INT8_QUANTIZED",
        "p95_latency_budget_ms": 12.0,
        "max_batch_size": 32,
        "description": "Review aspect sentiment analysis model"
    },
    "clip_visual_verifier_v1": {
        "framework": "TensorRT / Triton",
        "precision": "FP16",
        "p95_latency_budget_ms": 8.0,
        "max_batch_size": 16,
        "description": "CLIP photo clustering & quality filter"
    }
}


def get_model_metadata(model_name: str) -> Dict[str, Any]:
    return MODEL_REGISTRY.get(model_name, {})
