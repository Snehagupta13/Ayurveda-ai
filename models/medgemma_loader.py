"""
MedGemma Model Loader
Loads and manages the MedGemma language model for medical/health domain tasks
"""

from typing import Optional
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class MedGemmaLoader:
    """Loader for MedGemma model"""

    def __init__(
        self,
        model_name: str = "google/medgemma-2b-it",
        device: str = "cpu"
    ):
        """
        Initialize MedGemma loader

        Args:
            model_name: Hugging Face model id
            device: Device to load model on (cpu/cuda)
        """
        self.model_name = model_name
        self.device = device
        self.model: Optional[AutoModelForCausalLM] = None
        self.tokenizer: Optional[AutoTokenizer] = None

    def load_model(self) -> None:
        """Load MedGemma model and tokenizer"""
        if self.model is not None and self.tokenizer is not None:
            return

        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
            trust_remote_code=True
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            device_map=self.device,
            torch_dtype=torch.float32,
            trust_remote_code=True
        )

        self.model.eval()

    def get_model(self):
        """
        Get loaded model

        Returns:
            Loaded model instance
        """
        if self.model is None:
            self.load_model()
        return self.model

    def get_tokenizer(self):
        """
        Get tokenizer

        Returns:
            Tokenizer instance
        """
        if self.tokenizer is None:
            self.load_model()
        return self.tokenizer

    def generate_response(self, prompt: str, max_length: int = 512) -> str:
        """
        Generate response using MedGemma

        Args:
            prompt: Input prompt
            max_length: Maximum response length

        Returns:
            Generated response
        """
        if self.model is None or self.tokenizer is None:
            self.load_model()

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt"
        )

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_length,
                do_sample=False,          # deterministic (important for medical)
                temperature=0.0,
                eos_token_id=self.tokenizer.eos_token_id
            )

        return self.tokenizer.decode(
            outputs[0],
            skip_special_tokens=True
        )

    def unload_model(self) -> None:
        """Unload model to free memory"""
        if self.model is not None:
            del self.model
            self.model = None

        if self.tokenizer is not None:
            del self.tokenizer
            self.tokenizer = None

        torch.cuda.empty_cache()
