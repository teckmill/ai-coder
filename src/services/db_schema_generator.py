import json
import logging
from typing import Dict, List, Optional

from .base_service import BaseService

logger = logging.getLogger(__name__)


class DBSchemaGenerator(BaseService):
    """Generates and manages database schemas."""

    def __init__(self, model_name: str = "codellama"):
        """Initialize the database schema generator."""
        super().__init__(model_name=model_name)
        self.supported_databases = ["postgresql", "mysql", "sqlite", "mongodb"]
        self.data_type_mappings = {
            "postgresql": {
                "string": "VARCHAR",
                "text": "TEXT",
                "integer": "INTEGER",
                "float": "REAL",
                "boolean": "BOOLEAN",
                "date": "DATE",
                "datetime": "TIMESTAMP",
                "binary": "BYTEA",
            },
            "mysql": {
                "string": "VARCHAR(255)",
                "text": "TEXT",
                "integer": "INT",
                "float": "FLOAT",
                "boolean": "TINYINT(1)",
                "date": "DATE",
                "datetime": "DATETIME",
                "binary": "BLOB",
            },
            "sqlite": {
                "string": "TEXT",
                "text": "TEXT",
                "integer": "INTEGER",
                "float": "REAL",
                "boolean": "INTEGER",
                "date": "TEXT",
                "datetime": "TEXT",
                "binary": "BLOB",
            },
        }

    async def generate_schema(self, description: str, database_type: str) -> Dict:
        """Generate a database schema from description."""
        try:
            if database_type not in self.supported_databases:
                raise ValueError(f"Unsupported database type: {database_type}")

            prompt = f"""Generate a database schema for a {database_type} database based on this description:
            
            {description}
            
            Please provide:
            1. Table definitions with columns and types
            2. Primary and foreign key relationships
            3. Indexes and constraints
            4. Sample data for testing
            
            Format the response as:
            TABLES:
            <json_schema>
            RELATIONSHIPS:
            <json_relationships>
            INDEXES:
            <json_indexes>
            SAMPLE_DATA:
            <json_data>
            """

            result = await self._get_llm_suggestions(prompt)

            # Parse the response
            schema = {}
            current_section = None
            current_content = []

            for line in result["explanation"].split("\n"):
                if line.endswith(":"):
                    if current_section and current_content:
                        try:
                            schema[current_section] = json.loads("\n".join(current_content))
                        except json.JSONDecodeError:
                            schema[current_section] = "\n".join(current_content)
                    current_section = line[:-1].lower()
                    current_content = []
                elif current_section:
                    current_content.append(line)

            if current_section and current_content:
                try:
                    schema[current_section] = json.loads("\n".join(current_content))
                except json.JSONDecodeError:
                    schema[current_section] = "\n".join(current_content)

            return schema

        except Exception as e:
            logger.error(f"Error generating schema: {str(e)}")
            raise

    def generate_sql(self, schema: Dict, database_type: str) -> str:
        """Generate SQL statements from schema."""
        try:
            if database_type not in self.supported_databases or database_type == "mongodb":
                raise ValueError(f"SQL generation not supported for {database_type}")

            sql_statements = []
            type_mappings = self.data_type_mappings[database_type]

            # Create tables
            for table_name, table_def in schema["tables"].items():
                columns = []
                primary_key = None
                foreign_keys = []

                for col_name, col_def in table_def["columns"].items():
                    col_type = type_mappings.get(col_def["type"], "TEXT")
                    constraints = []

                    if col_def.get("required", False):
                        constraints.append("NOT NULL")
                    if col_def.get("unique", False):
                        constraints.append("UNIQUE")
                    if col_def.get("primary_key", False):
                        primary_key = col_name

                    column_def = f"{col_name} {col_type}"
                    if constraints:
                        column_def += f" {' '.join(constraints)}"
                    columns.append(column_def)

                if primary_key:
                    columns.append(f"PRIMARY KEY ({primary_key})")

                # Add foreign key constraints
                for rel in schema.get("relationships", []):
                    if rel["from_table"] == table_name:
                        from_col = rel["from_column"]
                        to_table = rel["to_table"]
                        to_col = rel["to_column"]
                        fk = f"FOREIGN KEY ({from_col}) REFERENCES {to_table}({to_col})"
                        foreign_keys.append(fk)

                # Create table statement
                table_body = ",\n    ".join(columns + foreign_keys)
                create_table = f"CREATE TABLE {table_name} (\n    {table_body}\n);"
                sql_statements.append(create_table)

            # Create indexes
            for index in schema.get("indexes", []):
                table_name = index["table"]
                column_name = index["column"]
                index_name = f"idx_{table_name}_{column_name}"
                create_index = f"CREATE INDEX {index_name} ON {table_name} ({column_name});"
                sql_statements.append(create_index)

            # Insert sample data
            if "sample_data" in schema:
                for table_name, records in schema["sample_data"].items():
                    for record in records:
                        columns = ", ".join(record.keys())
                        placeholders = ", ".join(f"'{str(v)}'" for v in record.values())
                        insert = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders});"
                        sql_statements.append(insert)

            return "\n\n".join(sql_statements)

        except Exception as e:
            logger.error(f"Error generating SQL: {str(e)}")
            raise

    def generate_orm_models(self, schema: Dict, orm_type: str) -> Dict:
        """Generate ORM models from schema."""
        try:
            if orm_type not in ["sqlalchemy", "django", "mongoose"]:
                raise ValueError(f"Unsupported ORM type: {orm_type}")

            schema_json = json.dumps(schema, indent=2)
            prompt = (
                f"Generate {orm_type} ORM models for this schema:\n\n"
                f"{schema_json}\n\n"
                "Please provide:\n"
                "1. Model definitions\n"
                "2. Relationships and foreign keys\n"
                "3. Validation rules\n"
                "4. Indexes and constraints\n\n"
                "Format as proper Python/JavaScript code based on the ORM."
            )

            result = self._get_llm_suggestions(prompt)
            return {
                "models": result["code"],
                "suggestions": result.get("suggestions", []),
                "warnings": result.get("warnings", []),
            }

        except Exception as e:
            logger.error(f"Error generating ORM models: {str(e)}")
            raise

    async def analyze_schema(self, schema: Dict) -> Dict:
        """Analyze schema for potential issues and optimizations."""
        try:
            prompt = f"""Analyze this database schema for issues and optimizations:
            
            {json.dumps(schema, indent=2)}
            
            Please identify:
            1. Normalization issues
            2. Performance considerations
            3. Scalability concerns
            4. Security considerations
            5. Best practices recommendations
            
            Format the response as:
            NORMALIZATION:
            <issues>
            PERFORMANCE:
            <considerations>
            SCALABILITY:
            <concerns>
            SECURITY:
            <considerations>
            RECOMMENDATIONS:
            <list>
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
                elif current_section:
                    current_content.append(line)

            if current_section and current_content:
                analysis[current_section] = "\n".join(current_content)

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing schema: {str(e)}")
            raise
