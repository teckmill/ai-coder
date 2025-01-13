from typing import Dict, List, Optional
import os
import json
from pathlib import Path
import logging
from .base_service import BaseService

logger = logging.getLogger(__name__)


class ProjectGenerator(BaseService):
    """Generates project structures and boilerplate code."""

    def __init__(self, model_name: str = "codellama"):
        """Initialize the project generator."""
        super().__init__(model_name=model_name)
        self.templates_dir = Path("templates/project_structures")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self._load_default_templates()

    def _load_default_templates(self):
        """Load default project structure templates."""
        default_templates = {
            "python-fastapi": {
                "name": "FastAPI Project",
                "description": "Modern FastAPI project with SQLAlchemy and testing",
                "structure": {
                    "app": {
                        "api": {
                            "v1": {
                                "endpoints": {},
                                "models.py": "",
                                "schemas.py": "",
                                "deps.py": "",
                            },
                            "__init__.py": "",
                        },
                        "core": {"config.py": "", "security.py": "", "__init__.py": ""},
                        "db": {"base.py": "", "session.py": "", "__init__.py": ""},
                        "__init__.py": "",
                        "main.py": "",
                    },
                    "tests": {"conftest.py": "", "__init__.py": ""},
                    ".env.example": "",
                    "README.md": "",
                    "requirements.txt": "",
                    "docker-compose.yml": "",
                    "Dockerfile": "",
                },
            },
            "react-typescript": {
                "name": "React TypeScript Project",
                "description": "Modern React project with TypeScript and testing",
                "structure": {
                    "src": {
                        "components": {"common": {}, "layout": {}, "__tests__": {}},
                        "hooks": {},
                        "pages": {},
                        "services": {},
                        "styles": {},
                        "types": {},
                        "utils": {},
                        "App.tsx": "",
                        "index.tsx": "",
                    },
                    "public": {"index.html": "", "favicon.ico": ""},
                    ".env.example": "",
                    "README.md": "",
                    "package.json": "",
                    "tsconfig.json": "",
                    "jest.config.js": "",
                    ".gitignore": "",
                },
            },
        }

        for template_id, template in default_templates.items():
            template_file = self.templates_dir / f"{template_id}.json"
            if not template_file.exists():
                with open(template_file, "w") as f:
                    json.dump(template, f, indent=2)

    async def generate_project_structure(
        self,
        project_type: str,
        project_name: str,
        description: str,
        features: List[str],
    ) -> Dict:
        """Generate a project structure with customized boilerplate code."""
        try:
            # Load base template
            template_file = self.templates_dir / f"{project_type}.json"
            if not template_file.exists():
                raise ValueError(f"Project type '{project_type}' not found")

            with open(template_file, "r") as f:
                template = json.load(f)

            # Generate customized structure
            prompt = f"""Generate a project structure for:
            Project Name: {project_name}
            Description: {description}
            Type: {project_type}
            Features: {', '.join(features)}
            
            Base structure:
            {json.dumps(template['structure'], indent=2)}
            
            Please provide:
            1. Additional directories and files needed for the features
            2. Content for key files (main entry points, README, configuration)
            3. Dependencies required for the features
            
            Format the response as:
            STRUCTURE: <json_structure>
            FILES:
            [filename1]
            <content1>
            [filename2]
            <content2>
            DEPENDENCIES:
            <dependencies_list>
            """

            result = await self._get_llm_suggestions(prompt)

            # Parse the response
            response_parts = result["explanation"].split("STRUCTURE:")
            if len(response_parts) > 1:
                structure_parts = response_parts[1].split("FILES:")
                structure = json.loads(structure_parts[0].strip())

                files_parts = structure_parts[1].split("DEPENDENCIES:")
                files_content = {}
                current_file = None
                current_content = []

                for line in files_parts[0].strip().split("\n"):
                    if line.startswith("[") and line.endswith("]"):
                        if current_file and current_content:
                            files_content[current_file] = "\n".join(current_content)
                        current_file = line[1:-1]
                        current_content = []
                    elif current_file:
                        current_content.append(line)

                if current_file and current_content:
                    files_content[current_file] = "\n".join(current_content)

                dependencies = files_parts[1].strip().split("\n")

                return {
                    "name": project_name,
                    "description": description,
                    "type": project_type,
                    "features": features,
                    "structure": structure,
                    "files": files_content,
                    "dependencies": dependencies,
                }
            else:
                raise ValueError("Invalid AI response format")

        except Exception as e:
            logger.error(f"Error generating project structure: {str(e)}")
            raise

    async def create_project(self, output_dir: str, project_config: Dict) -> Dict:
        """Create the project files and directories."""
        try:
            output_path = Path(output_dir) / project_config["name"]

            # Create directories
            def create_structure(base_path: Path, structure: Dict):
                for name, content in structure.items():
                    path = base_path / name
                    if isinstance(content, dict):
                        path.mkdir(parents=True, exist_ok=True)
                        create_structure(path, content)
                    else:
                        path.parent.mkdir(parents=True, exist_ok=True)
                        if name in project_config["files"]:
                            path.write_text(project_config["files"][name])
                        else:
                            path.touch()

            create_structure(output_path, project_config["structure"])

            return {
                "path": str(output_path),
                "files_created": len(project_config["files"]),
                "dependencies": project_config["dependencies"],
            }

        except Exception as e:
            logger.error(f"Error creating project: {str(e)}")
            raise
