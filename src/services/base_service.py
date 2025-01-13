from typing import Dict, Optional
import logging
from langchain_community.llms import Ollama

logger = logging.getLogger(__name__)

class BaseService:
    """Base class for AI services with model selection."""
    
    MODELS = {
        "codellama": {
            "name": "codellama",
            "description": "Meta's Code Llama model, optimized for code generation and analysis",
            "context_length": 4096,
            "strengths": [
                "Code completion and generation",
                "Multiple programming languages",
                "Technical documentation",
                "Code analysis"
            ],
            "setup": """
            1. Install Ollama: https://ollama.ai/
            2. Run: ollama pull codellama
            3. Start the model with: ollama run codellama
            """
        },
        "llama2": {
            "name": "llama2",
            "description": "Meta's general-purpose language model",
            "context_length": 4096,
            "strengths": [
                "Natural language understanding",
                "Context-aware responses",
                "Knowledge-based tasks",
                "Instruction following"
            ],
            "setup": """
            1. Install Ollama: https://ollama.ai/
            2. Run: ollama pull llama2
            3. Start the model with: ollama run llama2
            """
        },
        "mistral": {
            "name": "mistral",
            "description": "Mistral AI's powerful and efficient language model",
            "context_length": 8192,
            "strengths": [
                "Fast inference",
                "High-quality output",
                "Long context understanding",
                "Technical tasks"
            ],
            "setup": """
            1. Install Ollama: https://ollama.ai/
            2. Run: ollama pull mistral
            3. Start the model with: ollama run mistral
            """
        },
        "deepseek-coder": {
            "name": "deepseek-coder",
            "description": "DeepSeek's specialized code generation model",
            "context_length": 4096,
            "strengths": [
                "Code generation",
                "Bug fixing",
                "Code explanation",
                "Technical documentation"
            ],
            "setup": """
            1. Install Ollama: https://ollama.ai/
            2. Run: ollama pull deepseek-coder
            3. Start the model with: ollama run deepseek-coder
            """
        }
    }
    
    def __init__(self, model_name: str = "codellama"):
        """Initialize the service with a specific model."""
        self.model_name = model_name
        self._init_model()
    
    def _init_model(self):
        """Initialize the language model."""
        try:
            self.llm = Ollama(model=self.model_name)
            logger.info(f"Initialized {self.model_name} model")
        except Exception as e:
            logger.error(f"Error initializing {self.model_name}: {str(e)}")
            raise
    
    def set_model(self, model_name: str):
        """Change the current model."""
        if model_name not in self.MODELS:
            raise ValueError(f"Unsupported model: {model_name}")
        
        self.model_name = model_name
        self._init_model()
    
    @classmethod
    def get_available_models(cls) -> Dict:
        """Get information about available models."""
        return cls.MODELS
    
    async def _get_llm_suggestions(self, prompt: str) -> Dict:
        """Get suggestions from the language model."""
        try:
            response = await self.llm.agenerate([prompt])
            return {
                "explanation": response.generations[0][0].text,
                "model": self.model_name
            }
        except Exception as e:
            logger.error(f"Error getting suggestions from {self.model_name}: {str(e)}")
            raise
