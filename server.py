from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from src.services.code_generator import CodeGenerator
from src.services.code_analyzer import CodeAnalyzer

app = FastAPI()
code_generator = CodeGenerator()
code_analyzer = CodeAnalyzer()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str = ""
    prompt: str = ""

@app.post("/generate")
async def generate_code(request: CodeRequest):
    try:
        generated_code = code_generator.generate(request.prompt)
        return {"code": generated_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze")
async def analyze_code(request: CodeRequest):
    try:
        analysis = code_analyzer.analyze(request.code)
        return {"analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/refactor")
async def refactor_code(request: CodeRequest):
    try:
        refactored = code_generator.refactor(request.code)
        return {"refactored": refactored}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/explain")
async def explain_code(request: CodeRequest):
    try:
        explanation = code_analyzer.explain(request.code)
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
