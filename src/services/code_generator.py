from typing import Dict, Optional, Any
import os
import logging
import requests
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
import torch
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from src.services.base_service import BaseService
from src.config.models import LOCAL_MODELS, CLOUD_MODELS
import openai
import anthropic
from .usage_tracker import UsageTracker, ModelCosts
from .pricing import PricingManager
from .ai_coder_model import AiCoderModel

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

class ModelProvider:
    """Base class for different model providers."""
    def generate(self, prompt: str, **kwargs) -> str:
        raise NotImplementedError

class OpenAIProvider(ModelProvider):
    """Provider for OpenAI models."""
    def __init__(self, api_key: str, model: str = "gpt-4-turbo-preview"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model

    def generate(self, prompt: str, **kwargs) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=kwargs.get('temperature', 0.7),
            max_tokens=kwargs.get('max_tokens', 2000)
        )
        return response.choices[0].message.content

class AnthropicProvider(ModelProvider):
    """Provider for Anthropic models."""
    def __init__(self, api_key: str, model: str = "claude-3-opus-20240229"):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model

    def generate(self, prompt: str, **kwargs) -> str:
        response = self.client.messages.create(
            model=self.model,
            max_tokens=kwargs.get('max_tokens', 2000),
            temperature=kwargs.get('temperature', 0.7),
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

class OllamaProvider(ModelProvider):
    """Provider for Ollama models."""
    def __init__(self, model: str = "codellama", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host

    def generate(self, prompt: str, **kwargs) -> str:
        response = requests.post(
            f"{self.host}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "temperature": kwargs.get('temperature', 0.7),
                "max_tokens": kwargs.get('max_tokens', 2000)
            }
        )
        response.raise_for_status()
        return response.json()['response']

class HuggingFaceProvider(ModelProvider):
    """Provider for Hugging Face models."""
    def __init__(self, model_name: str = "bigcode/starcoder", device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            device_map=device,
            torch_dtype=torch.float16 if device == "cuda" else torch.float32
        )
        self.generator = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            device=device
        )

    def generate(self, prompt: str, **kwargs) -> str:
        response = self.generator(
            prompt,
            max_length=kwargs.get('max_tokens', 2000),
            temperature=kwargs.get('temperature', 0.7),
            num_return_sequences=1
        )
        return response[0]['generated_text'][len(prompt):]

class CodeGenerator(BaseService):
    """Service for generating code using AI models."""
    
    # Model providers and their configurations
    PROVIDER_MAP = {
        "gpt-4-turbo": (OpenAIProvider, {"requires_key": True}),
        "gpt-4": (OpenAIProvider, {"requires_key": True}),
        "gpt-3.5-turbo": (OpenAIProvider, {"requires_key": True}),
        "claude-3": (AnthropicProvider, {"requires_key": True}),
        "codellama-34b": (AiCoderModel, {"requires_key": False})  # Our free model
    }
    
    def __init__(self, user_id: str, tier: str = "free", model_name: str = "codellama-34b", api_key: Optional[str] = None):
        """Initialize the code generator service."""
        logger.debug(f"Initializing CodeGenerator with user_id={user_id}, tier={tier}, model={model_name}, has_api_key={bool(api_key)}")
        self.user_id = user_id
        self.tier = tier
        self.model_name = model_name
        self.api_key = api_key
        
        # Initialize services
        self.usage_tracker = UsageTracker(user_id)
        self.pricing_manager = PricingManager()
        
        # Initialize model provider
        self.provider = self._initialize_provider()
        self.model_available = True
    
    def _initialize_provider(self) -> ModelProvider:
        """Initialize the appropriate model provider."""
        if self.model_name not in self.PROVIDER_MAP:
            raise ValueError(f"Unsupported model: {self.model_name}")

        provider_class, config = self.PROVIDER_MAP[self.model_name]
        
        if config["requires_key"] and not self.api_key:
            raise ValueError(f"API key required for model: {self.model_name}")

        if provider_class == OpenAIProvider:
            return provider_class(api_key=self.api_key, model=self.model_name)
        elif provider_class == OllamaProvider:
            return provider_class(model=self.model_name)
        elif provider_class == HuggingFaceProvider:
            return provider_class(model_name=config.get("model_name", "bigcode/starcoder"))
        elif provider_class == AnthropicProvider:
            return provider_class(api_key=self.api_key, model=self.model_name)
        elif provider_class == AiCoderModel:
            return provider_class()
        
        raise ValueError(f"Unknown provider for model: {self.model_name}")

    @classmethod
    def get_model_types(cls) -> Dict[str, list]:
        """Get the available model types and their corresponding models."""
        return {
            "Local": list(LOCAL_MODELS.keys()),
            "Cloud": list(CLOUD_MODELS.keys())
        }

    async def generate(self, prompt: str, language: str = "python") -> Dict:
        """Generate code based on the prompt using the selected model"""
        try:
            # Check usage limits
            exceeded_limits = self.usage_tracker.check_limits(self.pricing_manager.get_tier_details(self.tier)["limits"])
            if exceeded_limits:
                return {
                    "error": "Usage limits exceeded",
                    "details": exceeded_limits,
                    "overage_charges": self.pricing_manager.calculate_overage_charges(
                        self.tier, 
                        self.usage_tracker.get_monthly_usage()
                    )
                }

            # Estimate complexity and select model
            complexity = self.usage_tracker.estimate_complexity(prompt)
            selected_model = self.usage_tracker.get_smart_model_selection("code", complexity)

            # Enhance prompt with language context
            enhanced_prompt = f"""Generate {language} code for: {prompt}
            Requirements:
            - Only return the code, no explanations
            - Include necessary imports
            - Follow best practices for {language}
            - Add brief comments for complex logic
            """
            
            # Generate code using the provider
            response = self.provider.generate(
                enhanced_prompt,
                model=selected_model,
                temperature=0.7,
                max_tokens=2000
            )

            # Track usage
            input_tokens = len(enhanced_prompt.split())  # Simple approximation
            output_tokens = len(response.split())
            cost = self.usage_tracker.add_usage(
                selected_model,
                input_tokens,
                output_tokens,
                "code"
            )

            # Get any usage alerts
            alerts = self.usage_tracker.get_usage_alerts()
            
            return {
                "code": response,
                "language": language,
                "model": selected_model,
                "cost": cost,
                "alerts": alerts
            }

        except Exception as e:
            logger.error(f"Error generating code: {str(e)}")
            raise

    def get_usage_stats(self) -> Dict:
        """Get current usage statistics."""
        monthly_usage = self.usage_tracker.get_monthly_usage()
        alerts = self.usage_tracker.get_usage_alerts()
        overage_charges = self.pricing_manager.calculate_overage_charges(
            self.tier,
            monthly_usage
        )

        return {
            "usage": monthly_usage,
            "alerts": alerts,
            "overage_charges": overage_charges,
            "tier": self.pricing_manager.get_tier_details(self.tier)
        }
