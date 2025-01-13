"""Model configurations for the AI Auto-Coder."""

# Define model configurations
LOCAL_MODELS = {
    "codellama": {"provider": "ollama", "name": "codellama"},
    "llama2": {"provider": "ollama", "name": "llama2"},
    "mistral": {"provider": "ollama", "name": "mistral"}
}

CLOUD_MODELS = {
    "gpt-4": {"provider": "openai", "name": "gpt-4"},
    "gpt-3.5-turbo": {"provider": "openai", "name": "gpt-3.5-turbo"},
    "claude-2": {"provider": "anthropic", "name": "claude-2"}
}
