from typing import Dict, Optional
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
        import openai
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
    """Service for generating code based on natural language descriptions."""
    
    PROVIDER_MAP = {
        "gpt-4-turbo-preview": (OpenAIProvider, {"requires_key": True}),
        "gpt-4": (OpenAIProvider, {"requires_key": True}),
        "gpt-3.5-turbo-16k": (OpenAIProvider, {"requires_key": True}),
        "gpt-3.5-turbo": (OpenAIProvider, {"requires_key": True}),
        "codellama": (OllamaProvider, {"requires_key": False}),
        "llama2": (OllamaProvider, {"requires_key": False}),
        "starcoder": (HuggingFaceProvider, {"requires_key": False, "model_name": "bigcode/starcoder"}),
        "codegen": (HuggingFaceProvider, {"requires_key": False, "model_name": "Salesforce/codegen-16B-mono"})
    }

    def __init__(self, model_name: str = "gpt-4-turbo-preview", api_key: Optional[str] = None):
        """Initialize the code generator service."""
        logger.debug(f"Initializing CodeGenerator with model={model_name}, has_api_key={bool(api_key)}")
        super().__init__(model_name=model_name, api_key=api_key)
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
            if not self.model_available:
                raise Exception("Model is not available. Please make sure it's installed and running.")
                
            template = """
            You are an expert web developer specializing in modern, beautiful web design. Generate code based on the following prompt.
            Language: {language}
            Prompt: {prompt}
            
            Follow these guidelines:
            1. Use modern HTML5 semantic elements
            2. Include CSS with:
               - Clean, modern typography
               - Pleasing color schemes
               - Responsive design
               - Smooth transitions/animations
               - Proper spacing and layout
            3. Add meta tags for SEO and mobile responsiveness
            4. Use CSS variables for consistent theming
            5. Include helpful comments
            6. Keep the code clean and maintainable
            
            If the prompt doesn't specify colors or styling, use an elegant modern design with:
            - A clean sans-serif font (e.g., Inter, Roboto)
            - A pleasing color palette
            - Subtle shadows and rounded corners
            - Proper whitespace and padding
            - Smooth hover effects
            
            Provide your response in the following format:
            CODE:
            <code here>
            EXPLANATION:
            <explanation here>
            """
            
            prompt_template = PromptTemplate(
                input_variables=["language", "prompt"],
                template=template
            )
            
            formatted_prompt = prompt_template.format(
                language=language,
                prompt=prompt
            )
            
            logger.debug("Sending request to model")
            response = self.provider.generate(formatted_prompt)
            logger.debug(f"Response received: {response}")
            
            # Parse response to extract code and explanation
            parts = response.split("CODE:")
            if len(parts) > 1:
                code_and_explanation = parts[1].split("EXPLANATION:")
                code = code_and_explanation[0].strip()
                explanation = code_and_explanation[1].strip() if len(code_and_explanation) > 1 else ""
                
                logger.debug(f"Extracted code: {code}")
                logger.debug(f"Extracted explanation: {explanation}")
                
                return {
                    "code": code,
                    "explanation": explanation
                }
            else:
                logger.error("Failed to parse model response")
                return {
                    "code": "Error: Could not generate code",
                    "explanation": "Failed to parse the model's response"
                }
                
        except Exception as e:
            logger.error(f"Code generation failed: {str(e)}", exc_info=True)
            return {
                "code": f"Error: {str(e)}",
                "explanation": "Code generation failed"
            }

    def generate_code(self, description: str) -> str:
        # Implement the logic to generate code based on the description
        # For now, let's return a placeholder string
        return f"Generated code for: {description}"

    @staticmethod
    def get_available_models(include_local: bool = False) -> Dict[str, Dict[str, Any]]:
        """Get available models and their configurations."""
        models = {
            "cloud": {
                "gpt-4-turbo-preview": "Latest & fastest GPT-4 model",
                "gpt-4": "Most capable GPT-4 model",
                "gpt-3.5-turbo-16k": "Extended context GPT-3.5",
                "gpt-3.5-turbo": "Fast and efficient GPT-3.5"
            }
        }
        
        if include_local:
            models["local"] = {
                "codellama": "Meta's CodeLlama model (requires Ollama)",
                "llama2": "Meta's Llama 2 model (requires Ollama)",
                "starcoder": "BigCode's StarCoder (requires GPU)",
                "codegen": "Salesforce CodeGen (requires GPU)"
            }
        
        return models
