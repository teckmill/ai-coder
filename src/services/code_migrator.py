import ast
import difflib
import logging
from typing import Dict, List, Optional

from .base_service import BaseService

logger = logging.getLogger(__name__)


class CodeMigrator(BaseService):
    """Assists in migrating code between different versions or frameworks."""

    def __init__(self):
        """Initialize the code migrator."""
        super().__init__()
        self.migration_rules = {
            "python2_to_3": {
                "print_statement": ("print ", "print("),
                "unicode": ("unicode", "str"),
                "long": ("long", "int"),
                "raw_input": ("raw_input", "input"),
                "xrange": ("xrange", "range"),
            },
            "react_class_to_hooks": {
                "lifecycle_methods": {
                    "componentDidMount": "useEffect(() => {}, [])",
                    "componentDidUpdate": "useEffect(() => {})",
                    "componentWillUnmount": "useEffect(() => { return () => {} }, [])",
                }
            },
        }

    async def analyze_code(
        self, code: str, source_version: str, target_version: str
    ) -> Dict:
        """Analyze code for migration issues."""
        try:
            prompt = f"""Analyze this code for migration from {source_version} to {target_version}:
            
            {code}
            
            Please identify:
            1. Breaking changes
            2. Deprecated features
            3. New features that could be used
            4. Performance implications
            5. Testing considerations
            
            Format the response as:
            BREAKING_CHANGES:
            <list>
            DEPRECATED:
            <list>
            NEW_FEATURES:
            <list>
            PERFORMANCE:
            <notes>
            TESTING:
            <notes>
            """

            result = await self._get_llm_suggestions(prompt)

            # Parse the response
            analysis = {}
            current_section = None
            current_content = []

            for line in result["explanation"].split("\n"):
                if line.endswith(":"):
                    if current_section and current_content:
                        analysis[current_section] = "\n".join(current_content)
                    current_section = line[:-1].lower()
                    current_content = []
                elif line.strip() and current_section:
                    current_content.append(line.strip())

            if current_section and current_content:
                analysis[current_section] = "\n".join(current_content)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing code: {str(e)}")
            raise

    async def migrate_code(
        self, code: str, source_version: str, target_version: str
    ) -> Dict:
        """Migrate code to target version."""
        try:
            # First analyze the code
            analysis = await self.analyze_code(code, source_version, target_version)

            # Generate migration prompt
            prompt = f"""Migrate this code from {source_version} to {target_version}:
            
            Original Code:
            {code}
            
            Analysis:
            {analysis}
            
            Please provide:
            1. Migrated code
            2. List of changes made
            3. Required dependency updates
            4. Migration notes
            
            Format the response as:
            CODE:
            <migrated_code>
            CHANGES:
            <list_of_changes>
            DEPENDENCIES:
            <dependency_updates>
            NOTES:
            <migration_notes>
            """

            result = await self._get_llm_suggestions(prompt)

            # Parse the response
            migration_result = {}
            current_section = None
            current_content = []

            for line in result["explanation"].split("\n"):
                if line.endswith(":"):
                    if current_section and current_content:
                        migration_result[current_section] = "\n".join(current_content)
                    current_section = line[:-1].lower()
                    current_content = []
                elif current_section:
                    current_content.append(line)

            if current_section and current_content:
                migration_result[current_section] = "\n".join(current_content)

            # Generate diff
            diff = list(
                difflib.unified_diff(
                    code.splitlines(keepends=True),
                    migration_result.get("code", "").splitlines(keepends=True),
                    fromfile=f"original ({source_version})",
                    tofile=f"migrated ({target_version})",
                )
            )

            migration_result["diff"] = "".join(diff)

            return migration_result

        except Exception as e:
            logger.error(f"Error migrating code: {str(e)}")
            raise

    async def generate_migration_guide(
        self, source_version: str, target_version: str, features: List[str]
    ) -> Dict:
        """Generate a migration guide for specific features."""
        try:
            prompt = f"""Create a migration guide from {source_version} to {target_version} 
            focusing on these features: {', '.join(features)}
            
            Please include:
            1. Step-by-step migration process
            2. Common pitfalls and solutions
            3. Best practices
            4. Testing strategies
            5. Rollback procedures
            
            Format the response as:
            STEPS:
            <numbered_steps>
            PITFALLS:
            <common_issues>
            BEST_PRACTICES:
            <practices>
            TESTING:
            <strategies>
            ROLLBACK:
            <procedures>
            """

            result = await self._get_llm_suggestions(prompt)

            # Parse the response
            guide = {}
            current_section = None
            current_content = []

            for line in result["explanation"].split("\n"):
                if line.endswith(":"):
                    if current_section and current_content:
                        guide[current_section] = "\n".join(current_content)
                    current_section = line[:-1].lower()
                    current_content = []
                elif current_section:
                    current_content.append(line)

            if current_section and current_content:
                guide[current_section] = "\n".join(current_content)

            return guide

        except Exception as e:
            logger.error(f"Error generating migration guide: {str(e)}")
            raise

    def apply_migration_rules(self, code: str, rule_set: str) -> str:
        """Apply predefined migration rules to code."""
        try:
            rules = self.migration_rules.get(rule_set)
            if not rules:
                raise ValueError(f"Rule set '{rule_set}' not found")

            migrated_code = code
            for rule_name, (old, new) in rules.items():
                if isinstance(old, str):
                    migrated_code = migrated_code.replace(old, new)
                elif callable(old):
                    migrated_code = old(migrated_code, new)

            return migrated_code

        except Exception as e:
            logger.error(f"Error applying migration rules: {str(e)}")
            raise
