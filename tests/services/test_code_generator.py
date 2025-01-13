import pytest
from unittest.mock import Mock, patch

from src.services.code_generator import CodeGenerator, OpenAIProvider, AnthropicProvider, AiCoderModel

@patch.dict('src.services.code_generator.LOCAL_MODELS', {})
def test_code_generator_initialization():
    """Test CodeGenerator initialization with default parameters."""
    mock_provider = Mock()
    mock_provider_map = {
        "ai_coder_v1": (AiCoderModel, {"requires_key": False}),
    }
    with patch.dict('src.services.code_generator.CodeGenerator.PROVIDER_MAP', mock_provider_map):
        generator = CodeGenerator(user_id="test_user")
        assert generator.user_id == "test_user"
        assert generator.tier == "hobby"
        assert generator.model_name == "ai_coder_v1"

@pytest.mark.asyncio
@patch('src.services.code_generator.OpenAIProvider')
@patch('src.services.pricing.PricingManager')
@patch('src.services.usage_tracker.UsageTracker')
@patch.dict('src.services.code_generator.LOCAL_MODELS', {})
@patch.dict('src.services.pricing.PricingManager.PRICING_TIERS', {'hobby': {}})
async def test_openai_provider_generation(mock_usage_tracker, mock_pricing_manager, mock_openai):
    """Test code generation using OpenAI provider."""
    # Setup mocks
    mock_instance = Mock()
    mock_instance.generate.return_value = "def test_function(): pass"
    mock_openai.return_value = mock_instance

    mock_pricing_manager.return_value.get_tier_details.return_value = {"limits": {}}
    mock_usage_tracker.return_value.check_limits.return_value = None
    mock_usage_tracker.return_value.estimate_complexity.return_value = "low"
    mock_usage_tracker.return_value.get_smart_model_selection.return_value = "gpt-4-turbo"
    mock_usage_tracker.return_value.add_usage.return_value = 0.0
    mock_usage_tracker.return_value.get_usage_alerts.return_value = []

    # Create mock provider map
    mock_provider_map = {
        "gpt-4-turbo": (mock_openai, {"requires_key": True}),
    }
    
    # Create generator with OpenAI
    with patch.dict('src.services.code_generator.CodeGenerator.PROVIDER_MAP', mock_provider_map):
        generator = CodeGenerator(
            user_id="test_user",
            model_name="gpt-4-turbo",
            api_key="test_key",
            tier="hobby"
        )
        
        # Test generation
        result = await generator.generate("Write a test function")
        assert isinstance(result, dict)
        assert "code" in result
        mock_instance.generate.assert_called_once()

@pytest.mark.asyncio
@patch('src.services.code_generator.AnthropicProvider')
@patch('src.services.pricing.PricingManager')
@patch('src.services.usage_tracker.UsageTracker')
@patch.dict('src.services.code_generator.LOCAL_MODELS', {})
@patch.dict('src.services.pricing.PricingManager.PRICING_TIERS', {'hobby': {}})
async def test_anthropic_provider_generation(mock_usage_tracker, mock_pricing_manager, mock_anthropic):
    """Test code generation using Anthropic provider."""
    # Setup mocks
    mock_instance = Mock()
    mock_instance.generate.return_value = "def example(): pass"
    mock_anthropic.return_value = mock_instance

    mock_pricing_manager.return_value.get_tier_details.return_value = {"limits": {}}
    mock_usage_tracker.return_value.check_limits.return_value = None
    mock_usage_tracker.return_value.estimate_complexity.return_value = "low"
    mock_usage_tracker.return_value.get_smart_model_selection.return_value = "claude-3"
    mock_usage_tracker.return_value.add_usage.return_value = 0.0
    mock_usage_tracker.return_value.get_usage_alerts.return_value = []

    # Create mock provider map
    mock_provider_map = {
        "claude-3": (mock_anthropic, {"requires_key": True}),
    }
    
    # Create generator with Anthropic
    with patch.dict('src.services.code_generator.CodeGenerator.PROVIDER_MAP', mock_provider_map):
        generator = CodeGenerator(
            user_id="test_user",
            model_name="claude-3",
            api_key="test_key",
            tier="hobby"
        )
        
        # Test generation
        result = await generator.generate("Write an example function")
        assert isinstance(result, dict)
        assert "code" in result
        mock_instance.generate.assert_called_once()

@patch.dict('src.services.code_generator.LOCAL_MODELS', {})
def test_invalid_model():
    """Test initialization with invalid model."""
    mock_provider_map = {
        "ai_coder_v1": (AiCoderModel, {"requires_key": False}),
    }
    with patch.dict('src.services.code_generator.CodeGenerator.PROVIDER_MAP', mock_provider_map):
        with pytest.raises(ValueError):
            CodeGenerator(
                user_id="test_user",
                model_name="invalid_model",
                tier="hobby"
            )
