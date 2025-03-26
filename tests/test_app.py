import pytest
from flask import json
import app
from unittest.mock import patch
from tests.test_config import TestConfig

def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get('/api/v1/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['version'] == '1.0.0'

@patch('app.Config', TestConfig)
def test_list_models(client):
    """Test listing available Mistral models."""
    response = client.get('/api/v1/models?provider=mistral')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['provider'] == 'mistral'
    assert 'models' in data
    assert isinstance(data['models'], list)
    assert 'mistral-large-latest' in data['models']
    assert data['default_model'] == 'mistral-large-latest'

def test_list_models_invalid_provider(client):
    """Test error handling for invalid provider."""
    response = client.get('/api/v1/models?provider=invalid')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

@patch('app.Config', TestConfig)
@patch('ai_utils.AIProvider.optimize_resume')
def test_optimize_resume_basic(mock_optimize, client, sample_resume):
    """Test basic resume optimization with required fields only."""
    mock_optimize.return_value = "Optimized resume content"
    
    response = client.post('/api/v1/optimize', 
                         json={'resume_content': sample_resume})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'optimized_content' in data
    assert data['provider'] == 'mistral'
    assert 'model' in data

@patch('app.Config', TestConfig)
@patch('ai_utils.AIProvider.optimize_resume')
def test_optimize_resume_with_guidelines(mock_optimize, client, sample_resume):
    """Test resume optimization with guidelines document."""
    mock_optimize.return_value = "Optimized resume content with guidelines"
    
    response = client.post('/api/v1/optimize', 
                         json={
                             'resume_content': sample_resume,
                             'guidelines': 'Focus on technical skills'
                         })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    mock_optimize.assert_called_with(sample_resume, 'Focus on technical skills', None)

@patch('app.Config', TestConfig)
@patch('ai_utils.AIProvider.optimize_resume')
def test_optimize_resume_with_custom_prompt(mock_optimize, client, sample_resume):
    """Test resume optimization with custom prompt."""
    mock_optimize.return_value = "Optimized resume content with custom prompt"
    
    response = client.post('/api/v1/optimize', 
                         json={
                             'resume_content': sample_resume,
                             'custom_prompt': 'Emphasize leadership experience'
                         })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    mock_optimize.assert_called_with(sample_resume, None, 'Emphasize leadership experience')

@patch('app.Config', TestConfig)
def test_optimize_resume_missing_content(client):
    """Test error handling for missing resume content."""
    response = client.post('/api/v1/optimize', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Resume content is required' in data['error']

@patch('app.Config', TestConfig)
def test_optimize_resume_empty_content(client):
    """Test error handling for empty resume content."""
    response = client.post('/api/v1/optimize', 
                         json={'resume_content': ''})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

@patch('app.Config', TestConfig)
def test_optimize_resume_large_content(client):
    """Test error handling for too large resume content."""
    # Make sure we're using TestConfig's MAX_INPUT_LENGTH
    large_content = 'x' * (TestConfig.MAX_INPUT_LENGTH + 1)
    response = client.post('/api/v1/optimize', 
                         json={'resume_content': large_content})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert f'Resume content must be between 1 and {TestConfig.MAX_INPUT_LENGTH} characters' in data['error']

@patch('app.Config', TestConfig)
@patch('ai_utils.AIProvider.optimize_resume')
def test_optimize_resume_api_error(mock_optimize, client, sample_resume):
    """Test error handling for AI service failure."""
    mock_optimize.side_effect = Exception("AI service error")
    
    response = client.post('/api/v1/optimize', 
                         json={'resume_content': sample_resume})
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

@pytest.mark.integration
def test_real_api_integration(client):
    """Test actual API integration with Mistral."""
    # Test resume optimization
    sample_resume = """
    John Doe
    Software Engineer
    
    Experience:
    - Python development
    - API design
    """
    
    response = client.post('/api/v1/optimize',
                         json={'resume_content': sample_resume})
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert isinstance(data['optimized_content'], str)
    assert data['provider'] == 'mistral'
    assert 'model' in data