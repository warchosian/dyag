"""
Trainer pour fine-tuning avec LoRA/PEFT.

Support:
- Fine-tuning multi-modeles (TinyLlama, llama3.2:1b, llama3.1:8b)
- Quantization 4-bit
- Checkpoint management
- Resume training
"""

import json
import torch
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime


class LoRATrainer:
    """Wrapper pour training LoRA avec PEFT."""

    # Formats de prompt par famille de modeles
    PROMPT_FORMATS = {
        'llama2': """<s>[INST] <<SYS>>
{system}
<</SYS>>

{user} [/INST] {assistant}</s>""",

        'llama3': """<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{assistant}<|eot_id|>""",

        'tinyllama': """<|system|>
{system}</s>
<|user|>
{user}</s>
<|assistant|>
{assistant}</s>""",

        'generic': """System: {system}

User: {user}
