import ast
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from .base_service import BaseService

logger = logging.getLogger(__name__)


class APIDocGenerator(BaseService):
    """Generates comprehensive API documentation."""

    def __init__(self, model_name: str = "codellama"):
        """Initialize the API documentation generator."""
        super().__init__(model_name=model_name)

    def _parse_fastapi_routes(self, file_path: str) -> List[Dict]:
        """Parse FastAPI routes from a Python file."""
        try:
            with open(file_path, "r") as f:
                code = f.read()

            tree = ast.parse(code)
            routes = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    decorators = [d for d in node.decorator_list if isinstance(d, ast.Call)]
                    for decorator in decorators:
                        if isinstance(decorator.func, ast.Attribute):
                            if decorator.func.attr in [
                                "get",
                                "post",
                                "put",
                                "delete",
                                "patch",
                            ]:
                                route = {
                                    "method": decorator.func.attr.upper(),
                                    "path": "",
                                    "name": node.name,
                                    "docstring": ast.get_docstring(node),
                                    "parameters": [],
                                    "response_model": None,
                                }

                                # Extract path from decorator
                                if decorator.args:
                                    route["path"] = decorator.args[0].value

                                # Extract parameters
                                for arg in node.args.args:
                                    if arg.annotation:
                                        route["parameters"].append(
                                            {
                                                "name": arg.arg,
                                                "type": ast.unparse(arg.annotation),
                                            }
                                        )

                                routes.append(route)

            return routes

        except Exception as e:
            logger.error(f"Error parsing FastAPI routes: {str(e)}")
            raise

    def _parse_openapi_spec(self, spec_path: str) -> Dict:
        """Parse OpenAPI specification file."""
        try:
            with open(spec_path, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error parsing OpenAPI spec: {str(e)}")
            raise

    async def generate_api_documentation(self, source_files: List[str], output_format: str = "markdown") -> Dict:
        """Generate API documentation from source files."""
        try:
            # Collect API information
            apis = []
            for file_path in source_files:
                if file_path.endswith(".py"):
                    routes = self._parse_fastapi_routes(file_path)
                    apis.extend(routes)
                elif file_path.endswith((".json", ".yaml", ".yml")):
                    spec = self._parse_openapi_spec(file_path)
                    # TODO: Convert OpenAPI spec to common format

            # Generate documentation
            prompt = f"""Generate {output_format} documentation for the following APIs:
            
            API Routes:
            {json.dumps(apis, indent=2)}
            
            Please include:
            1. Overview and authentication
            2. Detailed endpoint documentation
            3. Request/response examples
            4. Error handling
            5. Rate limiting and security considerations
            
            Format: {output_format}
            """

            result = await self._get_llm_suggestions(prompt)

            return {
                "documentation": result["explanation"],
                "format": output_format,
                "endpoints_documented": len(apis),
            }

        except Exception as e:
            logger.error(f"Error generating API documentation: {str(e)}")
            raise

    async def generate_postman_collection(self, apis: List[Dict]) -> Dict:
        """Generate a Postman collection for the APIs."""
        try:
            collection = {
                "info": {
                    "name": "API Collection",
                    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
                },
                "item": [],
            }

            for api in apis:
                item = {
                    "name": api["name"],
                    "request": {
                        "method": api["method"],
                        "header": [],
                        "url": {"raw": api["path"], "path": api["path"].split("/")[1:]},
                    },
                    "response": [],
                }

                # Generate example request/response
                prompt = f"""Generate example request and response for:
                Endpoint: {api['path']}
                Method: {api['method']}
                Parameters: {json.dumps(api['parameters'])}
                
                Please provide:
                1. Example request body (if applicable)
                2. Example response
                3. Example headers
                """

                result = await self._get_llm_suggestions(prompt)

                # Parse the response and add to collection
                # TODO: Parse AI response and add to Postman collection

                collection["item"].append(item)

            return collection

        except Exception as e:
            logger.error(f"Error generating Postman collection: {str(e)}")
            raise

    async def generate_swagger_spec(self, apis: List[Dict]) -> Dict:
        """Generate OpenAPI/Swagger specification."""
        try:
            spec = {
                "openapi": "3.0.0",
                "info": {"title": "API Documentation", "version": "1.0.0"},
                "paths": {},
            }

            for api in apis:
                path_item = {
                    api["method"].lower(): {
                        "summary": api["name"],
                        "description": api["docstring"],
                        "parameters": [],
                        "responses": {"200": {"description": "Successful response"}},
                    }
                }

                # Add parameters
                for param in api["parameters"]:
                    parameter = {
                        "name": param["name"],
                        "in": "query",  # Default to query, could be path/header/body
                        "required": True,
                        "schema": {"type": "string"},  # Default to string, could parse actual type
                    }
                    path_item[api["method"].lower()]["parameters"].append(parameter)

                spec["paths"][api["path"]] = path_item

            return spec

        except Exception as e:
            logger.error(f"Error generating Swagger spec: {str(e)}")
            raise
