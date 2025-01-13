from typing import Dict, Optional
import os
import logging
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

class CodeGenerator(BaseService):
    """Service for generating code based on natural language descriptions."""
    
    def __init__(self, model_name: str = "codellama", **kwargs):
        """Initialize the code generator service."""
        logger.debug(f"Initializing CodeGenerator with model={model_name}, kwargs={kwargs}")
        super().__init__(model_name=model_name, **kwargs)
        self.api_key = kwargs.get('api_key')
        self.initialize_model()
    
    def initialize_model(self):
        """Initialize the appropriate model based on model name."""
        try:
            logger.debug(f"Initializing model {self.model_name}")
            
            # Check if model is local or cloud-based
            if self.model_name in LOCAL_MODELS:
                logger.debug(f"Using local model {self.model_name}")
                self.llm = Ollama(model=self.model_name, temperature=0.1, timeout=120)
                self.model_available = True
            
            elif self.model_name in CLOUD_MODELS:
                if not self.api_key:
                    logger.error("API key required for cloud model but not provided")
                    raise ValueError(f"API key required for cloud model {self.model_name}")
                
                model_config = CLOUD_MODELS[self.model_name]
                logger.debug(f"Using cloud model {self.model_name} with provider {model_config['provider']}")
                
                if model_config['provider'] == 'openai':
                    self.llm = ChatOpenAI(model_name=self.model_name, temperature=0.1, 
                                        api_key=self.api_key)
                    self.model_available = True
                # Add support for other cloud providers here (anthropic, etc)
                else:
                    raise ValueError(f"Unsupported cloud provider for model {self.model_name}")
            
            else:
                raise ValueError(f"Unknown model: {self.model_name}")
            
            logger.debug(f"Successfully initialized {self.model_name} model")
        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}")
            self.model_available = False
            raise

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
            response = await self.llm.ainvoke(formatted_prompt)
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
