from typing import Optional, List, Dict
import anthropic
import openai
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from config import Config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIProvider:
    def __init__(self, provider: str = Config.DEFAULT_AI_PROVIDER, model: Optional[str] = None):
        self.provider = provider.lower()
        self._setup_client()
        
        # Get available models from the API
        self.available_models = self._fetch_available_models()
        
        # If no model specified, use the first available model (usually the latest)
        self.model = model or self.available_models[0] if self.available_models else None
        
        if not self.model:
            raise ValueError(f"No models available for provider '{self.provider}'")
        
        if self.model not in self.available_models:
            raise ValueError(f"Invalid model '{self.model}' for provider '{self.provider}'")

    def _setup_client(self):
        """Initialize the API client based on provider."""
        if self.provider == 'openai':
            openai.api_key = Config.OPENAI_API_KEY
        elif self.provider == 'anthropic':
            self.client = anthropic.Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        elif self.provider == 'mistral':
            self.client = MistralClient(api_key=Config.MISTRAL_API_KEY)
        else:
            raise ValueError(f"Unsupported AI provider: {self.provider}")

    def _fetch_available_models(self) -> List[str]:
        """Fetch available models directly from the provider's API."""
        try:
            if self.provider == 'openai':
                # Use OpenAI's models endpoint
                response = openai.models.list()
                models = [model.id for model in response.data 
                         if model.id.startswith(('gpt-4', 'gpt-3'))]
                logger.info(f"Fetched OpenAI models: {models}")
                return models

            elif self.provider == 'anthropic':
                # For Anthropic, models are properties of the client
                models = self.client.list_models()
                available_models = [model.id for model in models 
                                 if model.id.startswith('claude')]
                logger.info(f"Fetched Anthropic models: {available_models}")
                return available_models

            elif self.provider == 'mistral':
                # Use Mistral's models endpoint
                response = self.client.list_models()
                models = [model.id for model in response.data]
                logger.info(f"Fetched Mistral models: {models}")
                return models

        except Exception as e:
            logger.error(f"Error fetching models for {self.provider}: {str(e)}")
            # Fallback to default models if API call fails
            return self._get_fallback_models()

    def _get_fallback_models(self) -> List[str]:
        """Fallback model list in case API is unavailable."""
        fallbacks = {
            'openai': [
                'gpt-4-turbo-preview',
                'gpt-4',
                'gpt-3.5-turbo'
            ],
            'anthropic': [
                'claude-3-opus-20240229',
                'claude-3-sonnet-20240229',
                'claude-2.1'
            ],
            'mistral': [
                'mistral-large-latest',
                'mistral-medium-latest',
                'mistral-small-latest'
            ]
        }
        logger.warning(f"Using fallback models for {self.provider}")
        return fallbacks.get(self.provider, [])

    def optimize_resume(
        self,
        resume_content: str,
        guidelines: Optional[str] = None,
        job_description: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        base_prompt_path: str = "inputs/base_prompt.md"
    ) -> str:
        # Read base prompt from file
        try:
            with open(base_prompt_path, 'r', encoding='utf-8') as f:
                base_prompt = f.read()
        except FileNotFoundError:
            logger.error(f"Base prompt file not found: {base_prompt_path}")
            raise

        if job_description:
            base_prompt += (
                "Job Description to optimize for:\n"
                "```\n"
                f"{job_description}\n"
                "```\n\n"
           )

        if guidelines:
            base_prompt += (
                "Resume Guidelines:\n"
                "```\n"
                f"{guidelines}\n"
                "```\n\n"
                "Follow these guidelines strictly for formatting and structure.\n\n"
            )

        if custom_prompt:
            base_prompt += (
                "Custom prompt:\n"
                f"{custom_prompt}\n\n"
            )

        base_prompt += (
            "Resume content:\n"
            "```\n"
            f"{resume_content}\n"
            "```\n\n"
        )

        try:
            if self.provider == 'openai':
                response = openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a professional resume optimization assistant."},
                        {"role": "user", "content": base_prompt}
                    ],
                    temperature=0.7
                )
                return response.choices[0].message.content

            elif self.provider == 'anthropic':
                messages = [{
                    "role": "user",
                    "content": base_prompt
                }]
                response = self.client.messages.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.7
                )
                return response.content[0].text

            elif self.provider == 'mistral':
                messages = [
                    ChatMessage(role="system", content="You are a professional resume optimization assistant."),
                    ChatMessage(role="user", content=base_prompt)
                ]
                response = self.client.chat(
                    model=self.model,
                    messages=messages,
                    temperature=0.7
                )
                return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error optimizing resume with {self.provider} ({self.model}): {str(e)}")
            raise Exception(f"Error optimizing resume with {self.provider} ({self.model}): {str(e)}")

    def get_available_models(self) -> List[str]:
        """Get list of available models for the current provider."""
        return self.available_models

    def get_current_model(self) -> str:
        """Get the currently selected model."""
        return self.model

    def __call__(
        self,
        resume_content: str,
        guidelines: Optional[str] = None,
        job_description: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        base_prompt_path: str = "inputs/base_prompt.md"
    ) -> str:
        return self.optimize_resume(
            resume_content,
            guidelines=guidelines,
            job_description=job_description,
            custom_prompt=custom_prompt,
            base_prompt_path=base_prompt_path
        )