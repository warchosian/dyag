"""
Registry des modèles de base supportés pour le fine-tuning.

Ce module fournit:
- Liste des modèles supportés avec métadonnées
- Résolution des raccourcis vers chemins HuggingFace complets
- Informations sur les requirements matériels
"""

from typing import Dict, Any, Optional

# Registry des modèles de base supportés
SUPPORTED_BASE_MODELS: Dict[str, Dict[str, Any]] = {
    'tinyllama': {
        'hf_model': 'TinyLlama/TinyLlama-1.1B-Chat-v1.0',
        'params': '1.1B',
        'vram_min_gb': 2,
        'vram_recommended_gb': 4,
        'recommended_batch_size': 4,
        'recommended_lora_rank': 16,
        'cpu_acceptable': True,
        'description': 'Modèle léger, rapide, acceptable sur CPU'
    },
    'llama3.2:1b': {
        'hf_model': 'meta-llama/Llama-3.2-1B-Instruct',
        'params': '1B',
        'vram_min_gb': 3,
        'vram_recommended_gb': 6,
        'recommended_batch_size': 4,
        'recommended_lora_rank': 16,
        'cpu_acceptable': False,
        'description': 'Modèle recommandé, équilibre performance/coût'
    },
    'llama3.1:8b': {
        'hf_model': 'meta-llama/Llama-3.1-8B-Instruct',
        'params': '8B',
        'vram_min_gb': 12,
        'vram_recommended_gb': 16,
        'recommended_batch_size': 1,
        'recommended_lora_rank': 32,
        'cpu_acceptable': False,
        'description': 'Modèle puissant, nécessite GPU avec VRAM élevée'
    },
    'phi3': {
        'hf_model': 'microsoft/Phi-3-mini-4k-instruct',
        'params': '3.8B',
        'vram_min_gb': 6,
        'vram_recommended_gb': 8,
        'recommended_batch_size': 2,
        'recommended_lora_rank': 16,
        'cpu_acceptable': False,
        'description': 'Modèle Microsoft, bon compromis taille/performance'
    },
    'qwen2.5:1.5b': {
        'hf_model': 'Qwen/Qwen2.5-1.5B-Instruct',
        'params': '1.5B',
        'vram_min_gb': 3,
        'vram_recommended_gb': 6,
        'recommended_batch_size': 4,
        'recommended_lora_rank': 16,
        'cpu_acceptable': True,
        'description': 'Excellent modèle non-gated, meilleure qualité que TinyLlama'
    }
}


def resolve_base_model(model_name: str) -> str:
    """
    Résout un raccourci de modèle vers le chemin HuggingFace complet.

    Args:
        model_name: Raccourci (ex: 'tinyllama') ou chemin complet HF

    Returns:
        Chemin HuggingFace complet

    Examples:
        >>> resolve_base_model('tinyllama')
        'TinyLlama/TinyLlama-1.1B-Chat-v1.0'

        >>> resolve_base_model('meta-llama/Llama-3.2-1B-Instruct')
        'meta-llama/Llama-3.2-1B-Instruct'
    """
    if model_name in SUPPORTED_BASE_MODELS:
        return SUPPORTED_BASE_MODELS[model_name]['hf_model']
    return model_name  # Assume it's already a HF model path


def get_model_info(model_name: str) -> Optional[Dict[str, Any]]:
    """
    Récupère les informations d'un modèle.

    Args:
        model_name: Raccourci ou chemin HF du modèle

    Returns:
        Dict avec infos du modèle, ou None si non trouvé

    Examples:
        >>> info = get_model_info('llama3.2:1b')
        >>> info['vram_min_gb']
        3
    """
    if model_name in SUPPORTED_BASE_MODELS:
        return SUPPORTED_BASE_MODELS[model_name]

    # Recherche inverse par chemin HF
    for shortcut, info in SUPPORTED_BASE_MODELS.items():
        if info['hf_model'] == model_name:
            return info

    return None


def list_supported_models() -> Dict[str, str]:
    """
    Liste tous les modèles supportés.

    Returns:
        Dict {raccourci: description}
    """
    return {
        shortcut: info['description']
        for shortcut, info in SUPPORTED_BASE_MODELS.items()
    }


def recommend_batch_size(model_name: str, vram_gb: float) -> int:
    """
    Recommande un batch_size en fonction du modèle et de la VRAM disponible.

    Args:
        model_name: Nom du modèle
        vram_gb: VRAM disponible en GB

    Returns:
        Batch size recommandé
    """
    info = get_model_info(model_name)
    if not info:
        return 1  # Conservative default

    # Si VRAM insuffisante
    if vram_gb < info['vram_min_gb']:
        return 1  # Minimum absolu

    # Si VRAM largement suffisante
    if vram_gb >= info['vram_recommended_gb'] * 1.5:
        return info['recommended_batch_size'] * 2

    # Recommandation standard
    if vram_gb >= info['vram_recommended_gb']:
        return info['recommended_batch_size']

    # Entre min et recommended : proportionnel
    ratio = (vram_gb - info['vram_min_gb']) / (info['vram_recommended_gb'] - info['vram_min_gb'])
    return max(1, int(info['recommended_batch_size'] * ratio))
