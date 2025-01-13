import logging
from typing import Dict, Optional

from .base_service import BaseService

logger = logging.getLogger(__name__)


class GitHelper(BaseService):
    """Service for Git-related operations and suggestions."""

    def generate_commit_message(self, diff: str) -> Dict:
        """Generate a meaningful commit message from code changes."""
        try:
            prompt = f"""
            Generate a clear and descriptive git commit message for these code changes.
            Follow these commit message guidelines:
            1. Use imperative mood ("Add feature" not "Added feature")
            2. Keep first line under 50 characters
            3. Provide detailed description after blank line
            4. Reference any relevant issue numbers
            5. Categorize the change (feat, fix, docs, etc.)
            
            Code changes:
            {diff}
            
            Format the response as:
            - First line: Short summary
            - Blank line
            - Detailed description
            - Footer with metadata
            """

            response = self._get_llm_suggestions(prompt)

            return {
                "commit_message": response.get("explanation", ""),
                "type": self._determine_commit_type(diff),
                "scope": self._determine_commit_scope(diff),
            }
        except Exception as e:
            logger.error(f"Error generating commit message: {str(e)}", exc_info=True)
            raise

    def suggest_code_review_comments(self, diff: str) -> Dict:
        """Generate helpful code review comments."""
        try:
            prompt = f"""
            Review these code changes and provide constructive feedback on:
            1. Code quality and style
            2. Potential bugs or issues
            3. Performance implications
            4. Security considerations
            5. Testing requirements
            
            Code changes:
            {diff}
            
            Provide specific, actionable review comments.
            """

            response = self._get_llm_suggestions(prompt)

            return {
                "review_comments": response.get("explanation", ""),
                "suggestions": response.get("code", ""),
                "priority": self._determine_review_priority(diff),
            }
        except Exception as e:
            logger.error(f"Error generating review comments: {str(e)}", exc_info=True)
            raise

    def _determine_commit_type(self, diff: str) -> str:
        """Determine the type of commit (feat, fix, etc.)."""
        if "test" in diff.lower():
            return "test"
        elif "fix" in diff.lower() or "bug" in diff.lower():
            return "fix"
        elif "doc" in diff.lower():
            return "docs"
        else:
            return "feat"

    def _determine_commit_scope(self, diff: str) -> Optional[str]:
        """Determine the scope of the commit."""
        if "test" in diff.lower():
            return "testing"
        elif "api" in diff.lower():
            return "api"
        elif "ui" in diff.lower():
            return "ui"
        return None

    def _determine_review_priority(self, diff: str) -> str:
        """Determine the priority of the code review."""
        if "security" in diff.lower() or "auth" in diff.lower():
            return "high"
        elif "fix" in diff.lower() or "bug" in diff.lower():
            return "medium"
        return "low"
