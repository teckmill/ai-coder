import ast
import cProfile
import io
import logging
import pstats
import time
from typing import Dict, List, Optional

from .base_service import BaseService

logger = logging.getLogger(__name__)


class PerformanceProfiler(BaseService):
    """Analyzes and optimizes code performance."""

    def __init__(self, model_name: str = "codellama"):
        """Initialize the performance profiler."""
        super().__init__(model_name=model_name)

    def _analyze_complexity(self, code: str) -> Dict:
        """Analyze code complexity using AST."""
        try:
            tree = ast.parse(code)
            complexity = {
                "loops": 0,
                "conditions": 0,
                "function_calls": 0,
                "nested_depth": 0,
                "hot_spots": [],
            }

            class ComplexityVisitor(ast.NodeVisitor):
                def __init__(self):
                    self.current_depth = 0
                    self.max_depth = 0

                def visit_For(self, node):
                    complexity["loops"] += 1
                    self.current_depth += 1
                    self.max_depth = max(self.max_depth, self.current_depth)
                    self.generic_visit(node)
                    self.current_depth -= 1

                def visit_While(self, node):
                    complexity["loops"] += 1
                    self.current_depth += 1
                    self.max_depth = max(self.max_depth, self.current_depth)
                    self.generic_visit(node)
                    self.current_depth -= 1

                def visit_If(self, node):
                    complexity["conditions"] += 1
                    self.current_depth += 1
                    self.max_depth = max(self.max_depth, self.current_depth)
                    self.generic_visit(node)
                    self.current_depth -= 1

                def visit_Call(self, node):
                    complexity["function_calls"] += 1
                    self.generic_visit(node)

            visitor = ComplexityVisitor()
            visitor.visit(tree)
            complexity["nested_depth"] = visitor.max_depth

            return complexity

        except Exception as e:
            logger.error(f"Error analyzing complexity: {str(e)}")
            raise

    def profile_code(self, code: str, test_input: Optional[Dict] = None) -> Dict:
        """Profile code execution using cProfile."""
        try:
            # Create a temporary function to profile
            namespace = {}
            exec(code, namespace)

            # Set up profiler
            pr = cProfile.Profile()

            # Start profiling
            pr.enable()

            # Execute the code
            if test_input:
                for func_name, args in test_input.items():
                    if func_name in namespace:
                        namespace[func_name](*args)
            else:
                # Execute the last defined function
                last_func = None
                for name, obj in namespace.items():
                    if callable(obj) and not name.startswith("__"):
                        last_func = obj
                if last_func:
                    last_func()

            # Stop profiling
            pr.disable()

            # Get stats
            s = io.StringIO()
            ps = pstats.Stats(pr, stream=s).sort_stats("cumulative")
            ps.print_stats()

            # Parse profiling results
            stats = []
            for line in s.getvalue().split("\n"):
                if "function calls" in line:
                    continue
                if line.strip() and not line.startswith("   "):
                    parts = line.split()
                    if len(parts) >= 6:
                        stats.append(
                            {
                                "ncalls": parts[0],
                                "tottime": float(parts[1]),
                                "percall": float(parts[2]),
                                "cumtime": float(parts[3]),
                                "percall_cum": float(parts[4]),
                                "filename_lineno_function": " ".join(parts[5:]),
                            }
                        )

            return {
                "execution_stats": stats[:10],  # Top 10 most time-consuming functions
                "total_time": sum(stat["tottime"] for stat in stats),
                "function_calls": len(stats),
            }

        except Exception as e:
            logger.error(f"Error profiling code: {str(e)}")
            raise

    async def optimize_performance(self, code: str, profile_results: Dict) -> Dict:
        """Generate optimization suggestions based on profiling results."""
        try:
            complexity = self._analyze_complexity(code)

            prompt = f"""Analyze and optimize this code based on profiling results:
            
            Code:
            {code}
            
            Profiling Results:
            {profile_results}
            
            Complexity Analysis:
            {complexity}
            
            Please provide:
            1. Optimized code
            2. Performance bottlenecks identified
            3. Optimization techniques applied
            4. Expected performance improvements
            5. Trade-offs and considerations
            
            Format the response as:
            CODE:
            <optimized_code>
            BOTTLENECKS:
            <list>
            OPTIMIZATIONS:
            <list>
            IMPROVEMENTS:
            <estimates>
            TRADE_OFFS:
            <considerations>
            """

            result = await self._get_llm_suggestions(prompt)

            # Parse the response
            optimization = {}
            current_section = None
            current_content = []

            for line in result["explanation"].split("\n"):
                if line.endswith(":"):
                    if current_section and current_content:
                        optimization[current_section] = "\n".join(current_content)
                    current_section = line[:-1].lower()
                    current_content = []
                elif current_section:
                    current_content.append(line)

            if current_section and current_content:
                optimization[current_section] = "\n".join(current_content)

            return optimization

        except Exception as e:
            logger.error(f"Error optimizing performance: {str(e)}")
            raise

    async def generate_performance_report(
        self, code: str, profile_results: Dict, optimization_results: Dict
    ) -> Dict:
        """Generate a comprehensive performance report."""
        try:
            prompt = f"""Create a performance report for this code:
            
            Original Code:
            {code}
            
            Profile Results:
            {profile_results}
            
            Optimization Results:
            {optimization_results}
            
            Please include:
            1. Executive summary
            2. Detailed performance analysis
            3. Optimization recommendations
            4. Implementation plan
            5. Monitoring suggestions
            
            Format as a professional report with sections and metrics.
            """

            result = await self._get_llm_suggestions(prompt)

            return {
                "report": result["explanation"],
                "metrics": {
                    "original_performance": profile_results.get("total_time", 0),
                    "estimated_improvement": optimization_results.get(
                        "improvements", "N/A"
                    ),
                    "complexity_score": sum(self._analyze_complexity(code).values()),
                },
            }

        except Exception as e:
            logger.error(f"Error generating performance report: {str(e)}")
            raise
