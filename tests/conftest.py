import pytest
from flask import Flask
from app import app as flask_app
from ai_utils import AIProvider

@pytest.fixture
def app():
    """Create and configure a test Flask application instance."""
    flask_app.config['TESTING'] = True
    return flask_app

@pytest.fixture
def client(app):
    """Create a test client for making HTTP requests."""
    return app.test_client()

@pytest.fixture
def sample_resume():
    """Provide a sample resume for testing."""
    return """
    John Doe
    Software Engineer
    
    Experience:
    - Developed web applications using Python and JavaScript
    - Led team of 3 developers on e-commerce project
    """

@pytest.fixture
def mock_mistral_response():
    """Mock Mistral API response."""
    return {
        "id": "resp-123",
        "object": "chat.completion",
        "created": 1679749192,
        "model": "mistral-large-latest",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Optimized resume content"
                },
                "finish_reason": "stop"
            }
        ],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }

@pytest.fixture
def mock_mistral_models():
    """Mock Mistral models response."""
    return {
        "object": "list",
        "data": [
            {"id": "mistral-large-latest"},
            {"id": "mistral-medium-latest"},
            {"id": "mistral-small-latest"}
        ]
    }