from typing import Dict, Optional
import os
import logging
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from .base_service import BaseService

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

load_dotenv()

class CodeGenerator(BaseService):
    """Service for generating code based on natural language descriptions."""
    
    def __init__(self, model_name: str = "codellama"):
        """Initialize the code generator service."""
        super().__init__(model_name=model_name)
        try:
            self.ollama = Ollama(model=model_name, temperature=0.1, timeout=120)
            self.model_available = True
            logger.debug("Successfully initialized Ollama model")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {str(e)}")
            self.model_available = False

    async def generate(self, prompt: str, language: str = "python") -> Dict:
        """Generate code based on the prompt using Ollama"""
        try:
            if not self.model_available:
                raise Exception("Ollama is not available. Please make sure it's installed and running.")
                
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
            
            logger.debug("Sending request to Ollama")
            response = await self.ollama.ainvoke(formatted_prompt)
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
                logger.error("Failed to parse Ollama response")
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
