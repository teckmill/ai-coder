# Model Providers Guide

AI Coder supports multiple model providers for code generation. While the Streamlit UI focuses on cloud models for simplicity, the underlying system supports various providers that you can use in your own applications.

## Supported Providers

### 1. OpenAI (Cloud)
- Default provider in the Streamlit UI
- Requires API key
- Models:
  - `gpt-4-turbo-preview`: Latest & fastest GPT-4 model
  - `gpt-4`: Most capable GPT-4 model
  - `gpt-3.5-turbo-16k`: Extended context GPT-3.5
  - `gpt-3.5-turbo`: Fast and efficient GPT-3.5

### 2. Ollama (Local)
- Requires Ollama installation
- No API key needed
- Models:
  - `codellama`: Meta's CodeLlama model
  - `llama2`: Meta's Llama 2 model

#### Setup Instructions:
1. Install Ollama from [ollama.ai](https://ollama.ai)
2. Pull desired models:
   ```bash
   ollama pull codellama
   ollama pull llama2
   ```
3. Start Ollama service

### 3. Hugging Face (Local)
- Requires Python packages and model downloads
- GPU recommended for better performance
- Models:
  - `starcoder`: BigCode's StarCoder
  - `codegen`: Salesforce CodeGen

#### Setup Instructions:
1. Install required packages:
   ```bash
   pip install torch transformers
   ```
2. Models will be downloaded automatically on first use

## Using Different Providers in Your Code

### Basic Usage
```python
from src.services.code_generator import CodeGenerator

# OpenAI
generator = CodeGenerator(model_name="gpt-4", api_key="your-api-key")

# Ollama
generator = CodeGenerator(model_name="codellama")  # No API key needed

# Hugging Face
generator = CodeGenerator(model_name="starcoder")  # No API key needed

# Generate code
result = generator.generate_code(
    prompt="Create a function to sort a list",
    language="python"
)
print(result["code"])
```

### Advanced Configuration

#### Ollama Custom Host
```python
from src.services.code_generator import CodeGenerator, OllamaProvider

provider = OllamaProvider(
    model="codellama",
    host="http://custom-host:11434"
)
```

#### Hugging Face with Custom Device
```python
from src.services.code_generator import CodeGenerator, HuggingFaceProvider

provider = HuggingFaceProvider(
    model_name="bigcode/starcoder",
    device="cuda:0"  # Specify GPU device
)
```

## Performance Considerations

1. **OpenAI (Cloud)**
   - Requires internet connection
   - Best performance and reliability
   - Pay per use

2. **Ollama (Local)**
   - No internet required after model download
   - Good performance on modern CPUs
   - Free to use
   - Memory usage varies by model

3. **Hugging Face (Local)**
   - No internet required after model download
   - Requires significant GPU memory
   - Free to use
   - Best performance with NVIDIA GPU

## Troubleshooting

### Ollama Issues
1. Check if Ollama service is running
2. Verify model is downloaded: `ollama list`
3. Check API accessibility: `curl http://localhost:11434/api/tags`

### Hugging Face Issues
1. Check GPU memory availability
2. Try using smaller models if out of memory
3. Use `device="cpu"` if no GPU available

## Security Notes

1. Keep API keys secure
2. Local models may have different safety measures than cloud models
3. Consider rate limiting for production use
4. Review model outputs before executing generated code
