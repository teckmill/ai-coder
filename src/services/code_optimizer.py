from typing import Dict, List, Optional
import ast
import logging
from .base_service import BaseService

logger = logging.getLogger(__name__)


class CodeOptimizer(BaseService):
    """Service for optimizing code performance and structure."""

    def optimize_code(self, code: str, language: str) -> Dict:
        """Optimize code for better performance."""
        try:
            # Get optimization suggestions from LLM
            prompt = f"""
            Analyze this {language} code and suggest optimizations for:
            1. Performance improvements
            2. Memory efficiency
            3. Time complexity
            4. Space complexity
            5. Algorithm improvements
            
            Code to analyze:
            {code}
            
            Provide specific, actionable suggestions and optimized code.
            """

            response = self._get_llm_suggestions(prompt)

            # Parse static analysis results if Python
            static_analysis = {}
            if language.lower() == "python":
                static_analysis = self._analyze_python_code(code)

            return {
                "optimized_code": response.get("code", ""),
                "optimization_notes": response.get("explanation", ""),
                "static_analysis": static_analysis,
            }
        except Exception as e:
            logger.error(f"Error in code optimization: {str(e)}", exc_info=True)
            raise

    def _analyze_python_code(self, code: str) -> Dict:
        """Perform static analysis on Python code."""
        try:
            tree = ast.parse(code)
            analysis = {
                "complexity": self._analyze_complexity(tree),
                "memory_usage": self._analyze_memory_usage(tree),
                "bottlenecks": self._find_bottlenecks(tree),
            }
            return analysis
        except Exception as e:
            logger.error(f"Error in Python code analysis: {str(e)}", exc_info=True)
            return {}

    def _analyze_complexity(self, tree: ast.AST) -> List[Dict]:
        """Analyze code complexity."""
        issues = []
        for node in ast.walk(tree):
            # Check for nested loops
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, (ast.For, ast.While)) and child is not node:
                        issues.append(
                            {
                                "type": "complexity",
                                "message": "Nested loop detected - consider optimization",
                                "node": node,
                            }
                        )
        return issues

    def _analyze_memory_usage(self, tree: ast.AST) -> List[Dict]:
        """Analyze potential memory issues."""
        issues = []
        for node in ast.walk(tree):
            # Check for large list comprehensions
            if isinstance(node, ast.ListComp):
                if len(list(ast.walk(node))) > 10:
                    issues.append(
                        {
                            "type": "memory",
                            "message": "Large list comprehension - consider generator expression",
                            "node": node,
                        }
                    )
        return issues

    def _find_bottlenecks(self, tree: ast.AST) -> List[Dict]:
        """Identify potential performance bottlenecks."""
        issues = []
        for node in ast.walk(tree):
            # Check for repeated function calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    # TODO: Implement call frequency analysis
                    pass
        return issues
