"""
Core modules pour le fine-tuning.
"""

from .model_registry import SUPPORTED_BASE_MODELS, resolve_base_model, get_model_info
from .dataset_generators import DatasetGenerator, RuleBasedGenerator, LLMBasedGenerator, AugmentedGenerator
from .trainer import LoRATrainer

__all__ = [
    'SUPPORTED_BASE_MODELS',
    'resolve_base_model',
    'get_model_info',
    'DatasetGenerator',
    'RuleBasedGenerator',
    'LLMBasedGenerator',
    'AugmentedGenerator',
    'LoRATrainer',
]
