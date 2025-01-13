import logging
from typing import Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.services.code_analyzer import CodeAnalyzer
from src.services.code_generator import CodeGenerator
from src.services.code_optimizer import CodeOptimizer
from src.services.doc_generator import DocGenerator
from src.services.git_helper import GitHelper
from src.services.security_scanner import SecurityScanner
from src.services.template_manager import TemplateManager
from src.services.test_generator import TestGenerator

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Auto-Coder API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
code_generator = CodeGenerator()
code_analyzer = CodeAnalyzer()
code_optimizer = CodeOptimizer()
doc_generator = DocGenerator()
test_generator = TestGenerator()
security_scanner = SecurityScanner()
git_helper = GitHelper()
template_manager = TemplateManager()


# Request/Response Models
class CodeRequest(BaseModel):
    code: str
    language: str


class OptimizeRequest(BaseModel):
    code: str
    language: str
    optimization_level: Optional[str] = "medium"


class TestRequest(BaseModel):
    code: str
    language: str
    test_framework: Optional[str] = "pytest"


class DocRequest(BaseModel):
    code: str
    language: str
    doc_format: Optional[str] = "markdown"


class SecurityRequest(BaseModel):
    code: str
    language: str
    scan_level: Optional[str] = "high"


class GitRequest(BaseModel):
    diff: str
    scope: Optional[str] = None


class TemplateRequest(BaseModel):
    name: str
    code: str
    language: str
    description: str
    tags: List[str]


class TemplateUpdateRequest(BaseModel):
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None


class TemplateGenerateRequest(BaseModel):
    description: str
    language: str


@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "AI Auto-Coder API",
        "version": "2.0.0",
        "description": "AI-powered code generation and analysis",
    }


@app.post("/api/generate")
async def generate_code(request: CodeRequest):
    """Generate code based on natural language prompt."""
    try:
        return await code_generator.generate_code(request.code, request.language)
    except Exception as e:
        logger.error(f"Error in code generation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/analyze")
async def analyze_code(request: CodeRequest):
    """Analyze code and provide suggestions."""
    try:
        return await code_analyzer.analyze_code(request.code, request.language)
    except Exception as e:
        logger.error(f"Error in code analysis: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/optimize")
async def optimize_code(request: OptimizeRequest):
    """Optimize code for better performance."""
    try:
        return code_optimizer.optimize_code(request.code, request.language)
    except Exception as e:
        logger.error(f"Error in code optimization: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-docs")
async def generate_docs(request: DocRequest):
    """Generate documentation for code."""
    try:
        return doc_generator.generate_docs(request.code, request.language)
    except Exception as e:
        logger.error(f"Error in documentation generation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/generate-tests")
async def generate_tests(request: TestRequest):
    """Generate unit tests for code."""
    try:
        return test_generator.generate_tests(request.code, request.language)
    except Exception as e:
        logger.error(f"Error in test generation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/security-scan")
async def security_scan(request: SecurityRequest):
    """Scan code for security vulnerabilities."""
    try:
        return security_scanner.scan_code(request.code, request.language)
    except Exception as e:
        logger.error(f"Error in security scanning: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/commit-message")
async def generate_commit_message(request: GitRequest):
    """Generate Git commit message from diff."""
    try:
        return git_helper.generate_commit_message(request.diff)
    except Exception as e:
        logger.error(f"Error generating commit message: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/review-comments")
async def generate_review_comments(request: GitRequest):
    """Generate code review comments from diff."""
    try:
        return git_helper.suggest_code_review_comments(request.diff)
    except Exception as e:
        logger.error(f"Error generating review comments: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/templates")
async def get_templates(language: Optional[str] = None, tag: Optional[str] = None):
    """Get all templates, optionally filtered by language and/or tag."""
    try:
        return template_manager.get_templates(language, tag)
    except Exception as e:
        logger.error(f"Error getting templates: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/templates/{name}")
async def get_template(name: str):
    """Get a specific template by name."""
    template = template_manager.get_template(name)
    if template:
        return template
    raise HTTPException(status_code=404, detail="Template not found")


@app.post("/api/templates")
async def create_template(request: TemplateRequest):
    """Create a new template."""
    try:
        return template_manager.add_template(
            name=request.name,
            code=request.code,
            language=request.language,
            description=request.description,
            tags=request.tags,
        )
    except Exception as e:
        logger.error(f"Error creating template: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/templates/{name}")
async def update_template(name: str, request: TemplateUpdateRequest):
    """Update an existing template."""
    template = template_manager.update_template(
        name=name, code=request.code, description=request.description, tags=request.tags
    )
    if template:
        return template
    raise HTTPException(status_code=404, detail="Template not found")


@app.delete("/api/templates/{name}")
async def delete_template(name: str):
    """Delete a template."""
    if template_manager.delete_template(name):
        return {"message": "Template deleted"}
    raise HTTPException(status_code=404, detail="Template not found")


@app.post("/api/templates/generate")
async def generate_template(request: TemplateGenerateRequest):
    """Generate a new template using AI."""
    try:
        return await template_manager.generate_template(description=request.description, language=request.language)
    except Exception as e:
        logger.error(f"Error generating template: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
