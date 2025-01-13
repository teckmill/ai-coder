# AI-Powered Auto-Coder

An intelligent coding assistant that can write, improve, and analyze code using natural language prompts. This tool combines local LLM capabilities with optional cloud AI services to provide comprehensive coding assistance.

## Features

- **Code Generation**: Generate modern, maintainable code from natural language descriptions
- **Code Analysis**: Get detailed code analysis with suggestions for improvements
- **Code Templates**: Save and reuse code templates for common tasks
- **Project Generator**: Create project structures with customizable features
- **API Documentation**: Generate comprehensive API documentation
- **Performance Profiler**: Analyze and optimize code performance
- **Database Schema Generator**: Create and manage database schemas
- **Multiple Models**: Support for various Ollama models:
  - CodeLlama: Optimized for code generation
  - Llama2: General-purpose language model
  - Mistral: Fast and efficient model
  - DeepSeek Coder: Specialized code model

## Requirements

- Python 3.9+
- Ollama installed (https://ollama.ai/)
- One of the supported models:
  - codellama (recommended)
  - llama2
  - mistral
  - deepseek-coder

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-coder.git
cd ai-coder
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Ollama and download a model:
```bash
# Install Ollama from https://ollama.ai/
ollama pull codellama  # or another supported model
```

5. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Usage

### Running the Application
```bash
python -m streamlit run src/ui/streamlit_app.py
```

### Using Different Models

1. Select your preferred model from the sidebar
2. Follow the setup instructions for the selected model
3. The application will automatically use the selected model for all operations

### Features Guide

1. **Code Generation**
   - Enter a natural language description
   - Select the programming language
   - Get generated code with explanations

2. **Code Analysis**
   - Paste your code
   - Get detailed analysis of:
     - Code quality
     - Performance issues
     - Security concerns
     - Improvement suggestions

3. **Templates**
   - Browse existing templates
   - Create new templates
   - Generate templates using AI
   - Filter by language and tags

4. **Project Generator**
   - Describe your project
   - Select desired features
   - Get a complete project structure

5. **API Documentation**
   - Input your API code
   - Get comprehensive documentation
   - Multiple format support

6. **Performance Profiler**
   - Analyze code performance
   - Get optimization suggestions
   - View complexity analysis

7. **Database Schema**
   - Design database schemas
   - Generate SQL scripts
   - Create ORM models

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Streamlit and Langchain
- Powered by Ollama models
- Inspired by the open-source community
