# AI Coder VS Code Extension

Advanced AI-powered code generation and analysis extension for Visual Studio Code.

## Features

- **Code Generation**: Generate code snippets using natural language prompts
- **Code Analysis**: Get detailed analysis of your code
- **Code Refactoring**: AI-powered code refactoring suggestions
- **Code Explanation**: Get plain English explanations of complex code

## Commands

- `AI Coder: Generate Code` (Ctrl+Shift+G): Generate code from a natural language prompt
- `AI Coder: Analyze Code` (Ctrl+Shift+A): Analyze selected code
- `AI Coder: Refactor Code`: Get refactoring suggestions for selected code
- `AI Coder: Explain Code`: Get an explanation of selected code

## Requirements

- Visual Studio Code 1.85.0 or higher
- Node.js and npm installed
- Running AI Coder backend service

## Extension Settings

This extension contributes the following settings:

* `ai-coder.modelPath`: Path to the Ollama model
* `ai-coder.maxTokens`: Maximum number of tokens for code generation
* `ai-coder.temperature`: Temperature for code generation (0.0 - 1.0)

## Installation

1. Install the extension from the VS Code Marketplace
2. Configure the extension settings
3. Make sure the AI Coder backend service is running

## Development

1. Clone the repository
2. Run `npm install`
3. Press F5 to start debugging

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT
