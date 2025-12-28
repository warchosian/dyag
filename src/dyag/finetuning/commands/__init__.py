"""
Commandes CLI pour le fine-tuning.
"""

from .generate_training import register_generate_training_command
from .finetune import register_finetune_command
from .query_finetuned import register_query_finetuned_command
from .evaluate_finetuned import register_evaluate_finetuned_command
from .compare_models import register_compare_models_command

__all__ = [
    'register_generate_training_command',
    'register_finetune_command',
    'register_query_finetuned_command',
    'register_evaluate_finetuned_command',
    'register_compare_models_command',
]
