from typing import Dict, Optional

import black
from langchain_community.llms import Ollama


class CodeRefactor:
    def __init__(self):
        self.ollama = Ollama(model="llama3.2:3b")

    async def refactor(self, code: str, language: str = "python") -> Dict:
        """Refactor code for better quality and performance"""
        try:
            if language.lower() == "python":
                return await self._refactor_python(code)
            else:
                return await self._refactor_generic(code, language)
        except Exception as e:
            raise Exception(f"Code refactoring failed: {str(e)}")

    async def _refactor_python(self, code: str) -> Dict:
        """Refactor Python code using Black and AI suggestions"""
        try:
            # Format code using Black
            formatted_code = black.format_str(code, mode=black.FileMode())

            # Get AI suggestions for refactoring
            refactor_prompt = f"""
            Suggest improvements for this Python code to make it more efficient and maintainable:
            {formatted_code}
            
            Focus on:
            1. Code organization
            2. Performance optimization
            3. Design patterns
            4. Variable naming
            5. Documentation
            
            Provide the refactored code and explain the changes.
            """

            ai_response = self.ollama(refactor_prompt)

            # Parse AI response to extract code and explanation
            parts = ai_response.split("```python")
            if len(parts) > 1:
                refactored_code = parts[1].split("```")[0].strip()
                explanation = parts[0].strip() + "\n" + "".join(parts[2:]).strip()
            else:
                refactored_code = formatted_code
                explanation = ai_response

            return {
                "code": refactored_code,
                "explanation": explanation,
                "suggestions": self._parse_refactor_suggestions(ai_response),
            }

        except Exception as e:
            raise Exception(f"Python refactoring failed: {str(e)}")

    async def _refactor_generic(self, code: str, language: str) -> Dict:
        """Refactor code in other languages using AI"""
        try:
            refactor_prompt = f"""
            Suggest improvements for this {language} code to make it more efficient and maintainable:
            {code}
            
            Focus on:
            1. Code organization
            2. Performance optimization
            3. Design patterns
            4. Variable naming
            5. Documentation
            
            Provide the refactored code and explain the changes.
            """

            ai_response = self.ollama(refactor_prompt)

            # Parse AI response
            parts = ai_response.split(f"```{language}")
            if len(parts) > 1:
                refactored_code = parts[1].split("```")[0].strip()
                explanation = parts[0].strip() + "\n" + "".join(parts[2:]).strip()
            else:
                refactored_code = code
                explanation = ai_response

            return {
                "code": refactored_code,
                "explanation": explanation,
                "suggestions": self._parse_refactor_suggestions(ai_response),
            }

        except Exception as e:
            raise Exception(f"Generic refactoring failed: {str(e)}")

    def _parse_refactor_suggestions(self, ai_output: str) -> list:
        """Parse AI refactoring suggestions into structured format"""
        suggestions = []
        current_suggestion = ""

        for line in ai_output.split("\n"):
            if line.strip().startswith(("- ", "* ", "1. ")):
                if current_suggestion:
                    suggestions.append({"type": "refactor", "message": current_suggestion.strip()})
                current_suggestion = line.strip().lstrip("- *123456789. ")
            elif current_suggestion and line.strip():
                current_suggestion += " " + line.strip()

        if current_suggestion:
            suggestions.append({"type": "refactor", "message": current_suggestion.strip()})

        return suggestions
