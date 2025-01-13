from typing import Dict, List, Optional
import ast
import black
import logging
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from .base_service import BaseService

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CodeAnalyzer(BaseService):
    """Service for analyzing code and providing suggestions."""
    
    def __init__(self, model_name: str = "codellama:7b"):
        """Initialize the code analyzer service."""
        super().__init__(model_name=model_name)
        try:
            self.ollama = Ollama(model=model_name, temperature=0.1, timeout=120)  # Increase timeout and reduce temperature
            self.model_available = True
            logger.debug("Successfully initialized Ollama model")
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {str(e)}")
            self.model_available = False

    async def analyze(self, code: str, language: str = "python") -> Dict:
        """Analyze code for potential improvements"""
        try:
            logger.debug(f"Starting code analysis for language: {language}")
            logger.debug(f"Code to analyze: {code}")

            if language.lower() != "python":
                msg = f"Language {language} is not supported yet"
                logger.error(msg)
                raise Exception(msg)
                
            # Format code with black
            try:
                logger.debug("Formatting code with black")
                formatted_code = black.format_str(code, mode=black.Mode())
                logger.debug("Code formatting successful")
            except Exception as e:
                logger.warning(f"Black formatting failed: {str(e)}")
                formatted_code = code

            # Run Python analysis
            logger.debug("Starting AST analysis")
            analysis_output = self._analyze_python_code(formatted_code)
            logger.debug(f"Analysis output: {analysis_output}")
            
            # Get AI suggestions if available
            if self.model_available:
                logger.debug("Getting AI suggestions")
                ai_suggestions = await self._get_ai_suggestions(formatted_code, analysis_output)
                logger.debug(f"AI suggestions: {ai_suggestions}")
            else:
                logger.warning("AI suggestions not available - Ollama model not initialized")
                ai_suggestions = "AI suggestions not available - Ollama model not initialized"

            result = {
                "formatted_code": formatted_code,
                "linter_output": analysis_output,
                "ai_suggestions": ai_suggestions
            }
            logger.debug(f"Final analysis result: {result}")
            return result

        except Exception as e:
            logger.error(f"Python analysis failed: {str(e)}", exc_info=True)
            raise

    def _analyze_python_code(self, code: str) -> List[Dict]:
        """Analyze Python code using AST"""
        logger.debug("Starting AST-based code analysis")
        messages = []
        
        try:
            # Parse the code into an AST
            logger.debug("Parsing code into AST")
            tree = ast.parse(code)
            
            # Check for various code quality issues
            logger.debug("Running code quality checks")
            messages.extend(self._check_function_complexity(tree))
            messages.extend(self._check_variable_names(tree))
            messages.extend(self._check_imports(tree))
            messages.extend(self._check_docstrings(tree))
            
            logger.debug(f"Analysis complete. Found {len(messages)} issues")
            return messages
            
        except SyntaxError as e:
            logger.error(f"Syntax error in code: {str(e)}")
            return [{
                "type": "error",
                "line": e.lineno or 0,
                "column": e.offset or 0,
                "message": f"Syntax error: {str(e)}",
                "module": "syntax"
            }]
        except Exception as e:
            logger.error(f"Error during code analysis: {str(e)}", exc_info=True)
            return [{
                "type": "error",
                "line": 0,
                "column": 0,
                "message": f"Analysis error: {str(e)}",
                "module": "analyzer"
            }]

    def _check_function_complexity(self, tree: ast.AST) -> List[Dict]:
        """Check function complexity"""
        logger.debug("Checking function complexity")
        messages = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count number of statements
                body_nodes = list(ast.walk(node))
                if len(body_nodes) > 20:
                    messages.append({
                        "type": "convention",
                        "line": node.lineno,
                        "column": node.col_offset,
                        "message": f"Function '{node.name}' is too complex ({len(body_nodes)} nodes)",
                        "module": "complexity"
                    })
                
                # Check if function has a docstring
                if not ast.get_docstring(node):
                    messages.append({
                        "type": "convention",
                        "line": node.lineno,
                        "column": node.col_offset,
                        "message": f"Missing docstring for function '{node.name}'",
                        "module": "docstring"
                    })
        
        logger.debug(f"Function complexity check complete. Found {len(messages)} issues")
        return messages

    def _check_variable_names(self, tree: ast.AST) -> List[Dict]:
        """Check variable naming conventions"""
        logger.debug("Checking variable names")
        messages = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                # Check for single-letter variables (except i, j, k)
                if len(node.id) == 1 and node.id not in ['i', 'j', 'k']:
                    messages.append({
                        "type": "convention",
                        "line": node.lineno,
                        "column": node.col_offset,
                        "message": f"Single-letter variable name '{node.id}' should be more descriptive",
                        "module": "naming"
                    })
                
                # Check for snake_case naming convention
                if not node.id.islower() and '_' not in node.id:
                    messages.append({
                        "type": "convention",
                        "line": node.lineno,
                        "column": node.col_offset,
                        "message": f"Variable name '{node.id}' should use snake_case",
                        "module": "naming"
                    })
        
        logger.debug(f"Variable name check complete. Found {len(messages)} issues")
        return messages

    def _check_imports(self, tree: ast.AST) -> List[Dict]:
        """Check import statements"""
        logger.debug("Checking import statements")
        messages = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                # Check if imports are at the top level
                if node.lineno > 5:  # Allow for docstring and a few blank lines
                    messages.append({
                        "type": "convention",
                        "line": node.lineno,
                        "column": node.col_offset,
                        "message": "Import statement should be at the module level",
                        "module": "imports"
                    })
        
        logger.debug(f"Import check complete. Found {len(messages)} issues")
        return messages

    def _check_docstrings(self, tree: ast.AST) -> List[Dict]:
        """Check for missing docstrings"""
        logger.debug("Checking for missing docstrings")
        messages = []
        
        # Check module docstring
        if not ast.get_docstring(tree):
            messages.append({
                "type": "convention",
                "line": 1,
                "column": 0,
                "message": "Missing module docstring",
                "module": "docstring"
            })
        
        # Check class docstrings
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                if not ast.get_docstring(node):
                    messages.append({
                        "type": "convention",
                        "line": node.lineno,
                        "column": node.col_offset,
                        "message": f"Missing docstring for class '{node.name}'",
                        "module": "docstring"
                    })
        
        logger.debug(f"Docstring check complete. Found {len(messages)} issues")
        return messages

    async def _get_ai_suggestions(self, code: str, analysis_output: List[Dict]) -> str:
        """Get AI suggestions for code improvements"""
        logger.debug("Getting AI suggestions")
        try:
            template = """
            As an expert programmer, analyze this Python code and provide suggestions for improvement.
            Consider best practices, performance, and readability.

            CODE:
            {code}

            ANALYSIS ISSUES:
            {analysis_issues}

            Please provide specific suggestions for improvement, focusing on:
            1. Code structure and organization
            2. Performance optimizations
            3. Best practices
            4. Error handling
            5. Documentation

            Keep your response clear and concise.
            """
            
            # Format analysis issues
            analysis_issues_text = "\n".join([
                f"- {msg['type']}: {msg['message']} (line {msg['line']})"
                for msg in analysis_output
            ])
            
            prompt_template = PromptTemplate(
                input_variables=["code", "analysis_issues"],
                template=template
            )
            
            formatted_prompt = prompt_template.format(
                code=code,
                analysis_issues=analysis_issues_text if analysis_issues_text else "No issues found in analysis."
            )
            
            logger.debug("Sending request to Ollama")
            response = await self.ollama.ainvoke(formatted_prompt)
            logger.debug(f"AI suggestions received: {response.strip()}")
            return response.strip()
            
        except Exception as e:
            logger.error(f"Failed to get AI suggestions: {str(e)}")
            return f"Failed to get AI suggestions: {str(e)}"
