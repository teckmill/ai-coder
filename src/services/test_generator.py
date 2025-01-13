import ast
import logging
from typing import Dict, List

from .base_service import BaseService

logger = logging.getLogger(__name__)


class TestGenerator(BaseService):
    """Service for generating unit tests."""

    def generate_tests(self, code: str, language: str) -> Dict:
        """Generate unit tests for the given code."""
        try:
            # Get test cases from LLM
            prompt = f"""
            Generate comprehensive unit tests for this {language} code including:
            1. Test cases for normal scenarios
            2. Edge cases
            3. Error cases
            4. Integration tests if applicable
            5. Mocking examples where needed
            
            Code to test:
            {code}
            
            Provide complete test code with assertions and explanations.
            """

            response = self._get_llm_suggestions(prompt)

            # Parse testable components if Python
            components = {}
            if language.lower() == "python":
                components = self._analyze_testable_components(code)

            return {
                "test_code": response.get("code", ""),
                "test_explanation": response.get("explanation", ""),
                "testable_components": components,
            }
        except Exception as e:
            logger.error(f"Error in test generation: {str(e)}", exc_info=True)
            raise

    def _analyze_testable_components(self, code: str) -> Dict:
        """Analyze code for testable components."""
        try:
            tree = ast.parse(code)
            components = {
                "functions": self._get_testable_functions(tree),
                "classes": self._get_testable_classes(tree),
                "dependencies": self._get_dependencies(tree),
            }
            return components
        except Exception as e:
            logger.error(f"Error in testable components analysis: {str(e)}", exc_info=True)
            return {}

    def _get_testable_functions(self, tree: ast.AST) -> List[Dict]:
        """Extract testable function information."""
        functions = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_info = {
                    "name": node.name,
                    "args": self._get_function_params(node),
                    "returns": self._get_return_type(node),
                    "raises": self._get_potential_exceptions(node),
                    "complexity": self._estimate_complexity(node),
                }
                functions.append(func_info)
        return functions

    def _get_testable_classes(self, tree: ast.AST) -> List[Dict]:
        """Extract testable class information."""
        classes = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    "name": node.name,
                    "methods": self._get_testable_methods(node),
                    "attributes": self._get_class_attributes(node),
                    "dependencies": self._get_class_dependencies(node),
                }
                classes.append(class_info)
        return classes

    def _get_function_params(self, node: ast.FunctionDef) -> List[Dict]:
        """Extract function parameters for test case generation."""
        params = []
        for arg in node.args.args:
            param_info = {
                "name": arg.arg,
                "type": (self._get_annotation_name(arg.annotation) if arg.annotation else None),
                "has_default": any(d for d in node.args.defaults),
            }
            params.append(param_info)
        return params

    def _get_return_type(self, node: ast.FunctionDef) -> str:
        """Extract return type annotation."""
        if node.returns:
            return self._get_annotation_name(node.returns)
        return "Unknown"

    def _get_potential_exceptions(self, node: ast.FunctionDef) -> List[str]:
        """Identify potential exceptions that could be raised."""
        exceptions = []
        for child in ast.walk(node):
            if isinstance(child, ast.Raise):
                if isinstance(child.exc, ast.Name):
                    exceptions.append(child.exc.id)
        return exceptions

    def _estimate_complexity(self, node: ast.FunctionDef) -> str:
        """Estimate function complexity for test planning."""
        complexity = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While)):
                complexity += 1
        return "High" if complexity > 5 else "Medium" if complexity > 2 else "Low"

    def _get_testable_methods(self, node: ast.ClassDef) -> List[Dict]:
        """Extract testable method information from a class."""
        methods = []
        for child in node.body:
            if isinstance(child, ast.FunctionDef):
                method_info = {
                    "name": child.name,
                    "is_public": not child.name.startswith("_"),
                    "params": self._get_function_params(child),
                    "returns": self._get_return_type(child),
                }
                methods.append(method_info)
        return methods

    def _get_class_attributes(self, node: ast.ClassDef) -> List[str]:
        """Extract class attributes for test setup."""
        attributes = []
        for child in node.body:
            if isinstance(child, ast.AnnAssign):
                if isinstance(child.target, ast.Name):
                    attributes.append(child.target.id)
        return attributes

    def _get_class_dependencies(self, node: ast.ClassDef) -> List[str]:
        """Identify class dependencies for mocking."""
        dependencies = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                dependencies.append(base.id)
        return dependencies

    def _get_dependencies(self, tree: ast.AST) -> List[str]:
        """Extract code dependencies for test environment setup."""
        dependencies = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    dependencies.append(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    dependencies.append(node.module)
        return dependencies

    def _get_annotation_name(self, node: ast.AST) -> str:
        """Extract type annotation name."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Subscript):
            if isinstance(node.value, ast.Name):
                return f"{node.value.id}[...]"
        return "Unknown"
