from typing import Dict, Optional
import os
import logging
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from src.services.base_service import BaseService

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

class CodeGenerator(BaseService):
    """Service for generating code based on natural language descriptions."""
    
    AVAILABLE_MODELS = {
        "free": ["codellama", "llama2", "mistral"],
        "premium": ["gpt-4", "gpt-3.5-turbo", "claude-2"]
    }
    
    def __init__(self, model_name: str = "codellama", api_key: Optional[str] = None):
        """Initialize the code generator service."""
        super().__init__(model_name=model_name)
        self.model_name = model_name
        self.api_key = api_key
        self.initialize_model()
    
    def initialize_model(self):
        """Initialize the appropriate model based on model name."""
        try:
            if self.model_name in self.AVAILABLE_MODELS["free"]:
                self.llm = Ollama(model=self.model_name, temperature=0.1, timeout=120)
            elif self.model_name in self.AVAILABLE_MODELS["premium"]:
                if not self.api_key:
                    raise ValueError(f"API key required for premium model {self.model_name}")
                if "gpt" in self.model_name:
                    self.llm = ChatOpenAI(model_name=self.model_name, temperature=0.1, 
                                        api_key=self.api_key)
                # Add support for other premium models here
            else:
                raise ValueError(f"Unsupported model: {self.model_name}")
            
            self.model_available = True
            logger.debug(f"Successfully initialized {self.model_name} model")
        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}")
            self.model_available = False
            raise

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
