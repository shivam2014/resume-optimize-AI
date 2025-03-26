"""Test configuration module"""
import os
import pytest
from config import Config

class TestConfig:
    """Test configuration."""
    DEBUG = True
    TESTING = True
    MAX_INPUT_LENGTH = 5000
    DEFAULT_AI_PROVIDER = 'mistral'
    
    # Mock API keys and settings for testing
    MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY', 'test-mistral-key')
    MISTRAL_DEFAULT_MODEL = os.getenv('MISTRAL_DEFAULT_MODEL', 'mistral-large-latest')
    
    AVAILABLE_MODELS = {
        'mistral': {
            'models': ['mistral-large-latest', 'mistral-medium-latest', 'mistral-small-latest'],
            'default': 'mistral-large-latest'
        }
    }

    @staticmethod
    def get_available_models(provider):
        """Get available models for a provider."""
        return TestConfig.AVAILABLE_MODELS[provider]['models']

def test_get_default_model_with_env_var(monkeypatch):
    """Test get_default_model when environment variable is set."""
    test_model = "mistral-medium-latest"
    monkeypatch.setenv('MISTRAL_DEFAULT_MODEL', test_model)
    assert Config.get_default_model('mistral') == test_model

def test_get_default_model_fallback(monkeypatch):
    """Test get_default_model fallback to first available model."""
    monkeypatch.delenv('MISTRAL_DEFAULT_MODEL', raising=False)
    assert Config.get_default_model('mistral') == TestConfig.AVAILABLE_MODELS['mistral']['models'][0]

def test_get_default_model_invalid_provider():
    """Test get_default_model with invalid provider."""
    with pytest.raises(ValueError, match="Unsupported provider: invalid"):
        Config.get_default_model('invalid')