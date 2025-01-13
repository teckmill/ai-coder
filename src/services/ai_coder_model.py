"""AI Coder model implementation."""

import os
import sys
import logging
import torch
import torch.nn as nn
from typing import Optional, Dict, Any
from transformers import (
    PreTrainedModel,
    PreTrainedTokenizer,
    AutoTokenizer,
    AutoModelForCausalLM,
)

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
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

    def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError


class AiCoderModel(ModelProvider):
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

    def _setup_device(self) -> str:
        """Set up the device for model inference."""
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        return "cpu"

    def _get_default_model_path(self) -> str:
        """Get the default path for model weights."""
        return os.path.join(project_root, "src", "models", "ai_coder_v1")

    def _load_model(self) -> PreTrainedModel:
        """Load and configure the model with optimizations."""
        try:
            model_path = os.path.join(self.model_path)
            if not os.path.exists(model_path):
                raise ValueError(f"Model path not found: {model_path}")

            # Try loading with AutoModelForCausalLM first
            try:
                model = AutoModelForCausalLM.from_pretrained(
                    model_path, trust_remote_code=True, use_cache=True
                )
            except Exception as e:
                logger.warning(f"Failed to load with AutoModelForCausalLM: {str(e)}")
                # Fallback to CodeLlama model
                model = AutoModelForCausalLM.from_pretrained(
                    "codellama/CodeLlama-7b-Python",
                    trust_remote_code=True,
                    use_cache=True,
                )
                # Save it locally for future use
                model.save_pretrained(model_path)

            # Enable model optimizations
            if hasattr(model.config, "use_cache"):
                model.config.use_cache = True
            if hasattr(model.config, "gradient_checkpointing"):
                model.config.gradient_checkpointing = True
            if hasattr(model.config, "use_memory_efficient_attention"):
                model.config.use_memory_efficient_attention = True

            # Enable model parallelism if multiple GPUs are available
            if torch.cuda.device_count() > 1:
                model = torch.nn.DataParallel(model)

            model.to(self.device)
            return model

        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise

    def _load_tokenizer(self) -> PreTrainedTokenizer:
        """Load and configure the tokenizer."""
        try:
            # First try loading from local path
            tokenizer_path = os.path.join(self.model_path, "tokenizer")
            if os.path.exists(tokenizer_path):
                tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)
            else:
                # If no local tokenizer, use CodeLlama's tokenizer as base
                tokenizer = AutoTokenizer.from_pretrained(
                    "codellama/CodeLlama-7b-Python",
                    trust_remote_code=True,
                    padding_side="left",
                )
                # Save it locally for future use
                tokenizer.save_pretrained(tokenizer_path)

            # Add special tokens for code
            special_tokens = {
                "additional_special_tokens": [
                    "<code>",
                    "</code>",
                    "<python>",
                    "</python>",
                    "<javascript>",
                    "</javascript>",
                    "<error>",
                    "</error>",
                    "<suggestion>",
                    "</suggestion>",
                ]
            }
            tokenizer.add_special_tokens(special_tokens)

            # Ensure padding token exists
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            return tokenizer

        except Exception as e:
            logger.error(f"Error loading tokenizer: {str(e)}")
            raise

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate code based on the prompt."""
        try:
            # Prepare inputs
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=self.config.max_length,
            ).to(self.device)

            # Generate
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_length=self.config.max_length,
                    temperature=kwargs.get("temperature", self.config.temperature),
                    top_p=kwargs.get("top_p", self.config.top_p),
                    top_k=kwargs.get("top_k", self.config.top_k),
                    num_return_sequences=kwargs.get(
                        "num_return_sequences", self.config.num_return_sequences
                    ),
                    do_sample=kwargs.get("do_sample", self.config.do_sample),
                    pad_token_id=self.tokenizer.pad_token_id,
                    eos_token_id=self.tokenizer.eos_token_id,
                )

            # Decode and return
            generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            return generated_text[len(prompt) :]  # Remove the prompt from output

        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            raise
