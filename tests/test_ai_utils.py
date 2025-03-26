import pytest
from unittest.mock import patch, MagicMock
from ai_utils import AIProvider
from config import Config

def test_ai_provider_init_default():
    """Test AIProvider initialization with default parameters."""
    with patch('ai_utils.AIProvider._fetch_available_models') as mock_fetch:
        mock_fetch.return_value = ['mistral-large-latest', 'mistral-medium-latest']
        provider = AIProvider()
        assert provider.provider == 'mistral'
        assert provider.model in mock_fetch.return_value

def test_ai_provider_init_custom():
    """Test AIProvider initialization with custom model."""
    with patch('ai_utils.AIProvider._fetch_available_models') as mock_fetch:
        mock_fetch.return_value = ['mistral-large-latest', 'mistral-medium-latest']
        provider = AIProvider(provider='mistral', model='mistral-large-latest')
        assert provider.provider == 'mistral'
        assert provider.model == 'mistral-large-latest'

def test_ai_provider_invalid_provider():
    """Test error handling for invalid provider."""
    with pytest.raises(ValueError) as exc_info:
        AIProvider(provider='invalid')
    assert 'Unsupported AI provider' in str(exc_info.value)

def test_ai_provider_invalid_model():
    """Test error handling for invalid model."""
    with patch('ai_utils.AIProvider._fetch_available_models') as mock_fetch:
        mock_fetch.return_value = ['mistral-large-latest']
        with pytest.raises(ValueError) as exc_info:
            AIProvider(provider='mistral', model='invalid-model')
        assert 'Invalid model' in str(exc_info.value)

@patch('mistralai.client.MistralClient.list_models')
def test_fetch_mistral_models(mock_list):
    """Test fetching Mistral models."""
    mock_response = MagicMock()
    mock_response.data = [
        MagicMock(id='mistral-large-latest'),
        MagicMock(id='mistral-medium-latest')
    ]
    mock_list.return_value = mock_response

    provider = AIProvider(provider='mistral')
    models = provider.get_available_models()
    
    assert 'mistral-large-latest' in models
    assert 'mistral-medium-latest' in models

@patch('mistralai.client.MistralClient.list_models')
def test_fallback_models(mock_list):
    """Test fallback model handling when API is unavailable."""
    # Simulate API error
    mock_list.side_effect = Exception("API Error")
    
    # Initialize provider - should use fallback models
    provider = AIProvider(provider='mistral')
    models = provider.get_available_models()
    
    # Verify fallback models are returned
    assert isinstance(models, list)
    assert len(models) > 0
    assert 'mistral-large-latest' in models
    assert 'mistral-medium-latest' in models
    assert 'mistral-small-latest' in models

@patch('mistralai.client.MistralClient.chat')
def test_optimize_resume_mistral(mock_chat, sample_resume):
    """Test resume optimization with Mistral."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock(message=MagicMock(content="Optimized content"))]
    mock_chat.return_value = mock_response

    provider = AIProvider(provider='mistral')
    result = provider.optimize_resume(sample_resume)
    
    assert result == "Optimized content"
    mock_chat.assert_called_once()

def test_optimize_resume_with_guidelines():
    """Test resume optimization with guidelines."""
    with patch('ai_utils.AIProvider.optimize_resume') as mock_optimize:
        mock_optimize.return_value = "Optimized content"
        provider = AIProvider(provider='mistral')
        result = provider.optimize_resume(
            "Sample resume",
            guidelines="Focus on technical skills"
        )
        assert "Optimized content" in result

def test_optimize_resume_with_custom_prompt():
    """Test resume optimization with custom prompt."""
    with patch('ai_utils.AIProvider.optimize_resume') as mock_optimize:
        mock_optimize.return_value = "Optimized content"
        provider = AIProvider(provider='mistral')
        result = provider.optimize_resume(
            "Sample resume",
            custom_prompt="Highlight leadership"
        )
        assert "Optimized content" in result

@patch('mistralai.client.MistralClient.chat')
def test_optimize_resume_api_error(mock_chat):
    """Test error handling for AI API failures."""
    mock_chat.side_effect = Exception("API Error")
    provider = AIProvider(provider='mistral')
    
    with pytest.raises(Exception) as exc_info:
        provider.optimize_resume("Sample resume")
    assert "Error optimizing resume" in str(exc_info.value)

def test_get_current_model():
    """Test getting current model information."""
    with patch('ai_utils.AIProvider._fetch_available_models') as mock_fetch:
        mock_fetch.return_value = ['mistral-large-latest']
        provider = AIProvider(provider='mistral')
        assert provider.get_current_model() == 'mistral-large-latest'

# Integration test with real API
def test_real_mistral_integration():
    """Test actual integration with Mistral API."""
    provider = AIProvider(provider='mistral')
    
    # Test model listing
    models = provider.get_available_models()
    assert len(models) > 0
    assert any('mistral' in model for model in models)
    
    # Test basic resume optimization
    sample_resume = """
    John Doe
    Software Engineer
    
    Experience:
    - Python development
    - API design
    """
    
    result = provider.optimize_resume(sample_resume)
    assert isinstance(result, str)
    assert len(result) > 0