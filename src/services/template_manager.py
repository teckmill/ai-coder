from typing import Dict, List, Optional
import json
import os
from pathlib import Path
import logging
from .base_service import BaseService

logger = logging.getLogger(__name__)

class TemplateManager(BaseService):
    """Manages code templates."""
    
    def __init__(self, model_name: str = "codellama"):
        """Initialize the template manager."""
        super().__init__(model_name=model_name)
        self.templates_dir = Path("templates")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.templates_file = self.templates_dir / "templates.json"
        if not self.templates_file.exists():
            self._save_templates([])
    
    def _load_templates(self) -> List[Dict]:
        """Load templates from file."""
        try:
            if self.templates_file.exists():
                with open(self.templates_file, 'r') as f:
                    return json.load(f)
            return []
        except Exception as e:
            logger.error(f"Error loading templates: {str(e)}")
            return []
    
    def _save_templates(self, templates: List[Dict]) -> None:
        """Save templates to file."""
        try:
            with open(self.templates_file, 'w') as f:
                json.dump(templates, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving templates: {str(e)}")
    
    def list_templates(self, language: Optional[str] = None, 
                      tags: Optional[List[str]] = None) -> Dict[str, List[Dict]]:
        """List all templates, optionally filtered by language and tags."""
        try:
            templates = self._load_templates()
            
            if language and language != "All":
                templates = [t for t in templates if t.get("language") == language]
            
            if tags:
                templates = [t for t in templates if any(tag in t.get("tags", []) for tag in tags)]
            
            return {"templates": templates}
            
        except Exception as e:
            logger.error(f"Error listing templates: {str(e)}")
            return {"templates": []}
    
    def create_template(self, name: str, description: str, code: str,
                       language: str = "python", tags: Optional[List[str]] = None) -> Dict:
        """Create a new template."""
        try:
            templates = self._load_templates()
            
            # Check if template with same name exists
            if any(t["name"] == name for t in templates):
                raise ValueError(f"Template '{name}' already exists")
            
            new_template = {
                "name": name,
                "description": description,
                "code": code,
                "language": language,
                "tags": tags or []
            }
            
            templates.append(new_template)
            self._save_templates(templates)
            
            return new_template
            
        except Exception as e:
            logger.error(f"Error creating template: {str(e)}")
            raise
    
    def update_template(self, name: str, description: Optional[str] = None,
                       code: Optional[str] = None, language: Optional[str] = None,
                       tags: Optional[List[str]] = None) -> Dict:
        """Update an existing template."""
        try:
            templates = self._load_templates()
            
            # Find template
            template = next((t for t in templates if t["name"] == name), None)
            if not template:
                raise ValueError(f"Template '{name}' not found")
            
            # Update fields
            if description:
                template["description"] = description
            if code:
                template["code"] = code
            if language:
                template["language"] = language
            if tags:
                template["tags"] = tags
            
            self._save_templates(templates)
            
            return template
            
        except Exception as e:
            logger.error(f"Error updating template: {str(e)}")
            raise
    
    def delete_template(self, name: str) -> bool:
        """Delete a template."""
        try:
            templates = self._load_templates()
            
            # Find and remove template
            templates = [t for t in templates if t["name"] != name]
            self._save_templates(templates)
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting template: {str(e)}")
            return False
    
    async def generate_template(self, description: str, language: str = "python") -> Dict:
        """Generate a template from description using AI."""
        try:
            prompt = f"""Generate a code template based on this description:
            
            Description: {description}
            Language: {language}
            
            Please provide:
            1. A descriptive name for the template
            2. The template code
            3. Relevant tags
            4. Usage examples
            
            Format the response as:
            NAME:
            <template_name>
            CODE:
            <code>
            TAGS:
            <tag_list>
            EXAMPLES:
            <examples>
            """
            
            result = await self._get_llm_suggestions(prompt)
            
            # Parse the response
            template = {}
            current_section = None
            current_content = []
            
            for line in result["explanation"].split("\n"):
                if line.endswith(":"):
                    if current_section and current_content:
                        template[current_section.lower()] = "\n".join(current_content)
                    current_section = line[:-1]
                    current_content = []
                elif current_section:
                    current_content.append(line)
            
            if current_section and current_content:
                template[current_section.lower()] = "\n".join(current_content)
            
            # Create the template
            return self.create_template(
                name=template.get("name", "Generated Template"),
                description=description,
                code=template.get("code", ""),
                language=language,
                tags=template.get("tags", "").split(",")
            )
            
        except Exception as e:
            logger.error(f"Error generating template: {str(e)}")
            raise
