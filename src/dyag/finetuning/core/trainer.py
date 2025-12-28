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

    def __init__(
        self,
        base_model: str,
        dataset_path: str,
        output_dir: str,
        epochs: int = 3,
        batch_size: int = 4,
        lora_rank: int = 16,
        lora_alpha: int = 32,
        device: str = "auto",
        max_seq_length: int = 512
    ):
        """Initialise le trainer LoRA."""
        self.base_model = base_model
        self.dataset_path = dataset_path
        self.output_dir = output_dir
        self.epochs = epochs
        self.batch_size = batch_size
        self.lora_rank = lora_rank
        self.lora_alpha = lora_alpha
        self.max_seq_length = max_seq_length

        if device == "auto":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

    def detect_model_family(self) -> str:
        """Detecte la famille du modele pour adapter le format de prompt."""
        model_lower = self.base_model.lower()

        if "tinyllama" in model_lower:
            return "tinyllama"
        elif "llama-3" in model_lower or "llama3" in model_lower:
            return "llama3"
        elif "llama-2" in model_lower or "llama2" in model_lower:
            return "llama2"
        else:
            return "generic"

    def load_dataset(self) -> List[Dict]:
        """Charge le dataset JSONL."""
        data = []
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    data.append(json.loads(line))
        return data

    def format_prompt(self, messages: List[Dict]) -> str:
        """Formate les messages en prompt selon la famille du modele."""
        system_msg = next((m['content'] for m in messages if m['role'] == 'system'), '')
        user_msg = next((m['content'] for m in messages if m['role'] == 'user'), '')
        assistant_msg = next((m['content'] for m in messages if m['role'] == 'assistant'), '')

        family = self.detect_model_family()

        if family == "llama3":
            prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_msg}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_msg}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

{assistant_msg}<|eot_id|>"""

        elif family == "llama2":
            prompt = f"""<s>[INST] <<SYS>>
{system_msg}
<</SYS>>

{user_msg} [/INST] {assistant_msg}</s>"""

        elif family == "tinyllama":
            prompt = f"""<|system|>
{system_msg}</s>
<|user|>
{user_msg}</s>
<|assistant|>
{assistant_msg}</s>"""

        else:
            prompt = f"""System: {system_msg}

User: {user_msg}
Assistant: {assistant_msg}"""

        return prompt

    def prepare_dataset_for_training(self):
        """Prepare dataset with HuggingFace Dataset format."""
        from datasets import Dataset
        
        data = self.load_dataset()
        formatted_data = []
        
        for sample in data:
            text = self.format_prompt(sample["messages"])
            formatted_data.append({"text": text})
        
        return Dataset.from_list(formatted_data)

    def train(self) -> Dict[str, Any]:
        """Lance le training avec LoRA."""
        print("[INFO] Implementation complete du training en cours...")
        print("      Cette fonctionnalite necessite transformers, peft, trl")
        
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, BitsAndBytesConfig
            from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
            from trl import SFTTrainer
        except ImportError as e:
            raise ImportError(
                f"Dependances manquantes: {e}. "
                "Installez avec: pip install transformers peft trl accelerate bitsandbytes"
            )
        
        # Prepare dataset
        print("Preparation du dataset...")
        dataset = self.prepare_dataset_for_training()
        print(f"[OK] {len(dataset)} exemples prepares")
        
        # Load tokenizer
        print(f"Chargement du tokenizer: {self.base_model}")
        tokenizer = AutoTokenizer.from_pretrained(self.base_model)
        tokenizer.pad_token = tokenizer.eos_token
        tokenizer.padding_side = "right"
        
        # Quantization config (4-bit)
        if self.device == "cuda":
            bnb_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.float16,
                bnb_4bit_use_double_quant=True,
            )
            load_kwargs = {"quantization_config": bnb_config, "device_map": "auto"}
        else:
            load_kwargs = {"device_map": self.device}
        
        # Load model
        print(f"Chargement du modele: {self.base_model}")
        model = AutoModelForCausalLM.from_pretrained(self.base_model, **load_kwargs)
        
        if self.device == "cuda":
            model.gradient_checkpointing_enable()
            model = prepare_model_for_kbit_training(model)
        
        # LoRA config
        lora_config = LoraConfig(
            r=self.lora_rank,
            lora_alpha=self.lora_alpha,
            target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
            lora_dropout=0.05,
            bias="none",
            task_type="CAUSAL_LM"
        )
        
        model = get_peft_model(model, lora_config)
        print("[OK] Modele LoRA prepare")
        model.print_trainable_parameters()
        
        # Training args
        Path(self.output_dir).mkdir(parents=True, exist_ok=True)
        
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            num_train_epochs=self.epochs,
            per_device_train_batch_size=self.batch_size,
            gradient_accumulation_steps=4,
            gradient_checkpointing=True if self.device == "cuda" else False,
            optim="paged_adamw_32bit" if self.device == "cuda" else "adamw_torch",
            logging_steps=10,
            save_strategy="epoch",
            learning_rate=2e-4,
            max_grad_norm=0.3,
            warmup_ratio=0.03,
            lr_scheduler_type="cosine",
            fp16=False,
            bf16=False,
            report_to="none"
        )
        
        # Trainer
        # Note: model is already a PEFT model, so we don't pass peft_config again
        # In TRL 0.26+, tokenizer parameter is renamed to processing_class
        trainer = SFTTrainer(
            model=model,
            train_dataset=dataset,
            processing_class=tokenizer,
            args=training_args,
            formatting_func=lambda x: x["text"]  # Extract text field from dataset
        )
        
        # Train
        print("\nDemarrage du training...")
        start_time = datetime.now()
        trainer.train()
        end_time = datetime.now()
        
        # Save
        final_path = f"{self.output_dir}/final"
        trainer.model.save_pretrained(final_path)
        tokenizer.save_pretrained(final_path)
        
        duration = end_time - start_time
        print(f"\n[OK] Training termine en {duration}")
        print(f"Modele sauvegarde: {final_path}")
        
        return {
            "duration": str(duration),
            "output_path": final_path,
            "epochs": self.epochs
        }

    def resume(self, checkpoint_path: str) -> Dict[str, Any]:
        """Reprend depuis un checkpoint."""
        raise NotImplementedError("Resume pas encore implemente")
