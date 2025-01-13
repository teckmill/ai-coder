"""AI Coder model implementation."""

import logging
import os
import sys
from typing import Any, Dict, Optional

import torch
import torch.nn as nn
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
)

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

logger = logging.getLogger(__name__)

class ModelConfig:
    """Configuration for the AI Coder model."""

    def __init__(self):
        self.max_length = 2048
        self.temperature = 0.7
        self.top_p = 0.95
        self.top_k = 50
        self.num_return_sequences = 1
        self.do_sample = True


class ModelProvider:
    """Base class for model providers."""

    def generate(self, prompt: str, **kwargs):
        raise NotImplementedError


class AiCoderModel:
    """AI Coder model implementation."""

    def __init__(self, model_path: Optional[str] = None):
        """Initialize the AI Coder model.

        Args:
            model_path: Path to model files. If None, uses default path.
        """
        self.config = ModelConfig()
        self.model_path = model_path or self._get_default_model_path()
        self.device = self._setup_device()

        try:
            self.model = self._load_model()
            self.tokenizer = self._load_tokenizer()
            logger.info(f"Successfully loaded AI Coder model from {self.model_path}")
        except Exception as e:
            logger.error(f"Failed to load AI Coder model: {str(e)}")
            raise

    def _setup_device(self):
        """Set up the device for model inference."""
        if torch.cuda.is_available():
            device = torch.device("cuda")
            logger.info("Using CUDA for model inference")
        else:
            device = torch.device("cpu")
            logger.info("Using CPU for model inference")
        return device

    def _get_default_model_path(self):
        """Get the default path for model weights."""
        from config.models import LOCAL_MODELS

        if "ai_coder_v1" in LOCAL_MODELS:
            return LOCAL_MODELS["ai_coder_v1"]
        else:
            # Fallback to CodeLlama if local model not found
            return "codellama/CodeLlama-7b-hf"

    def _load_model(self):
        """Load and configure the model with optimizations."""
        try:
            model = AutoModelForCausalLM.from_pretrained(
                self.model_path,
                torch_dtype=(
                    torch.float16 if torch.cuda.is_available() else torch.float32
                ),
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True,
            )
            model.eval()
            return model
        except Exception as e:
            logger.error(f"Error loading model from {self.model_path}: {str(e)}")
            raise

    def _load_tokenizer(self):
        """Load and configure the tokenizer."""
        try:
            tokenizer = AutoTokenizer.from_pretrained(
                self.model_path,
                trust_remote_code=True,
            )
            tokenizer.pad_token = tokenizer.eos_token
            return tokenizer
        except Exception as e:
            logger.error(f"Error loading tokenizer from {self.model_path}: {str(e)}")
            raise

    def generate(self, prompt: str, **kwargs):
        """Generate code based on the prompt."""
        try:
            # Override default config with any provided kwargs
            generation_config = {
                "max_length": kwargs.pop("max_length", self.config.max_length),
                "temperature": kwargs.pop("temperature", self.config.temperature),
                "top_p": kwargs.pop("top_p", self.config.top_p),
                "top_k": kwargs.pop("top_k", self.config.top_k),
                "num_return_sequences": kwargs.pop(
                    "num_return_sequences", self.config.num_return_sequences
                ),
                "do_sample": kwargs.pop("do_sample", self.config.do_sample),
                "pad_token_id": self.tokenizer.pad_token_id,
                **kwargs,
            }

            # Tokenize input prompt
            inputs = self.tokenizer(prompt, return_tensors="pt", truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(**inputs, **generation_config)

            # Decode and return the generated text
            decoded_outputs = [
                self.tokenizer.decode(output, skip_special_tokens=True)
                for output in outputs
            ]

            return decoded_outputs[0] if len(decoded_outputs) == 1 else decoded_outputs

        except Exception as e:
            logger.error(f"Error during generation: {str(e)}")
            raise
