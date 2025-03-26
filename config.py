import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask config
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # AI API Keys
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

    # AI Settings
    DEFAULT_AI_PROVIDER = os.getenv('DEFAULT_AI_PROVIDER', 'mistral')
    MISTRAL_DEFAULT_MODEL = os.getenv('MISTRAL_DEFAULT_MODEL')  # Environment variable for default Mistral model
    MAX_INPUT_LENGTH = 15000  # Maximum characters for resume content

    # Supported AI Providers
    SUPPORTED_PROVIDERS = ['openai', 'anthropic', 'mistral']

    @classmethod
    def get_available_models(cls, provider: str) -> list:
        """Get available models for a provider."""
        from ai_utils import AIProvider
        if provider not in cls.SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")
        ai_provider = AIProvider(provider=provider)
        return ai_provider.get_available_models()

    @classmethod
    def get_default_model(cls, provider: str) -> str:
        """Get default model for a provider."""
        from ai_utils import AIProvider
        if provider not in cls.SUPPORTED_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")
            
        # Check for provider-specific default model
        if provider == 'mistral' and cls.MISTRAL_DEFAULT_MODEL:
            return cls.MISTRAL_DEFAULT_MODEL
            
        ai_provider = AIProvider(provider=provider)
        models = ai_provider.get_available_models()
        return models[0] if models else None

    @classmethod
    def validate_provider(cls, provider: str) -> bool:
        """Check if a provider is supported."""
        return provider.lower() in cls.SUPPORTED_PROVIDERS