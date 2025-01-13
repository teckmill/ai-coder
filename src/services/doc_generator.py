from typing import Dict, Optional
import ast
import logging
from .base_service import BaseService

logger = logging.getLogger(__name__)

class DocGenerator(BaseService):
    """Service for generating code documentation."""
    
    def generate_docs(self, code: str, language: str) -> Dict:
        """Generate comprehensive documentation for the code."""
        try:
            # Get documentation from LLM
            prompt = f"""
            Generate comprehensive documentation for this {language} code including:
            1. Overview and purpose
            2. Function/class documentation
            3. Parameters and return values
            4. Usage examples
            5. Dependencies
            6. Error handling
            
            Code to document:
            {code}
            
            Provide clear, detailed documentation following best practices.
            """
            
            response = self._get_llm_suggestions(prompt)
            
            # Parse code structure if Python
            structure = {}
            if language.lower() == "python":
                structure = self._analyze_python_structure(code)
            
            return {
                "documentation": response.get("explanation", ""),
                "code_structure": structure,
                "examples": response.get("code", "")
            }
        except Exception as e:
            logger.error(f"Error in documentation generation: {str(e)}", exc_info=True)
            raise
    
    def _analyze_python_structure(self, code: str) -> Dict:
        """Analyze Python code structure for documentation."""
        try:
            tree = ast.parse(code)
            structure = {
                "classes": self._get_classes(tree),
                "functions": self._get_functions(tree),
                "imports": self._get_imports(tree)
            }
            return structure
        except Exception as e:
            logger.error(f"Error in Python structure analysis: {str(e)}", exc_info=True)
            return {}
    
    def _get_classes(self, tree: ast.AST) -> list:
        """Extract class information."""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)],
                    "docstring": ast.get_docstring(node) or "",
                    "decorators": [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
                }
                classes.append(class_info)
        return classes
    
    def _get_functions(self, tree: ast.AST) -> list:
        """Extract function information."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    "name": node.name,
                    "args": self._get_function_args(node),
                    "docstring": ast.get_docstring(node) or "",
                    "returns": self._get_return_info(node),
                    "decorators": [d.id for d in node.decorator_list if isinstance(d, ast.Name)]
                }
                functions.append(func_info)
        return functions
    
    def _get_function_args(self, node: ast.FunctionDef) -> list:
        """Extract function arguments."""
        args = []
        for arg in node.args.args:
            arg_info = {
                "name": arg.arg,
                "annotation": arg.annotation.id if arg.annotation and hasattr(arg.annotation, 'id') else None
            }
            args.append(arg_info)
        return args
    
    def _get_return_info(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type information."""
        if node.returns and hasattr(node.returns, 'id'):
            return node.returns.id
        return None
    
    def _get_imports(self, tree: ast.AST) -> list:
        """Extract import information."""
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append({"name": name.name, "asname": name.asname})
            elif isinstance(node, ast.ImportFrom):
                for name in node.names:
                    imports.append({
                        "name": name.name,
                        "asname": name.asname,
                        "module": node.module
                    })
        return imports
