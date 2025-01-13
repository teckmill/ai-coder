# Contributing to AI-Coder

Thank you for your interest in contributing to AI-Coder! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

1. **Fork the Repository**
   - Fork the repository to your GitHub account
   - Clone your fork locally

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Development Setup**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows

   # Install dependencies
   pip install -r requirements.txt

   # Install Ollama and model
   ollama pull codellama
   ```

4. **Make Your Changes**
   - Write clear, concise commit messages
   - Follow the existing code style
   - Add tests if applicable
   - Update documentation as needed

5. **Test Your Changes**
   - Ensure all tests pass
   - Test with different models
   - Verify UI functionality

6. **Submit a Pull Request**
   - Push your changes to your fork
   - Create a pull request from your branch to our main branch
   - Describe your changes in detail
   - Reference any related issues

## Pull Request Guidelines

- Keep PRs focused on a single feature or bug fix
- Include screenshots for UI changes
- Update README.md if needed
- Ensure CI checks pass

## Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for functions and classes
- Keep functions focused and modular

## Reporting Issues

- Use the issue tracker
- Include steps to reproduce
- Specify your environment details
- Attach relevant logs

## Feature Requests

- Use the issue tracker with label "enhancement"
- Describe the feature in detail
- Explain why it would be useful
- Consider implementation complexity

## Questions?

Feel free to:
- Open an issue for questions
- Join our discussions
- Contact the maintainers

Thank you for contributing to AI-Coder!
