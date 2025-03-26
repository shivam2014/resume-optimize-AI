# Resume Optimization AI

An AI-powered resume optimization tool that leverages multiple AI providers to enhance resumes based on job descriptions and industry best practices.

## Features

- Support for multiple AI providers (Mistral, OpenAI, Anthropic, DeepSeek)
- Automatic PDF and document parsing
- Customizable optimization guidelines
- RESTful API interface
- Command-line demo tool 
- Output saved with timestamps
- Debug mode for detailed insights

## Setup

1. Clone the repository:
```bash
git clone https://github.com/shivam2014/resume-optimize-AI.git
cd resume-optimize-AI
```

2. Create and activate virtual environment using `uv`:
```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv .venv

# Activate on Windows (depends on cmd,powershell, git bash, etc..)
.venv\Scripts\activate

# Activate on Linux/Mac
source .venv/bin/activate
```

3. Install dependencies using `uv`:
```bash
# Install dependencies from requirements.txt
uv pip install -r requirements.txt

# Or use uv sync to install from lockfile
uv sync
```

4. Configure environment:
```bash
# Copy example config
cp .env.example .env

# Edit .env and add your API keys
```

## Environment Configuration

Required variables in `.env`:

- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key  
- `MISTRAL_API_KEY`: Mistral API key
- `DEEPSEEK_API_KEY`: DeepSeek API key
- `DEFAULT_AI_PROVIDER`: Default AI provider (mistral/openai/anthropic)
- `MISTRAL_DEFAULT_MODEL`: Default Mistral model (default: 'mistral-large-latest')

## Usage

### Demo Tool (demo.py)

The demo tool provides an easy way to optimize resumes using the command line:

```bash
uv run demo.py --resume resume.pdf \
    --guidelines inputs/RESUME_GUIDELINES.md \
    --job-description job_desc.txt \
    --model mistral-large-latest \
    --custom-prompt "Focus on technical skills" \
    --base-prompt inputs/base_prompt.md \
    --debug
```

#### Available Arguments

- `--resume` (required): Path to resume file (PDF/DOCX)
- `--guidelines`: Path to guidelines file (default: inputs/RESUME_GUIDELINES.md)
- `--model`: Specific AI model to use
- `--custom-prompt`: Additional instructions for optimization
- `--job-description`: Path to job description file
- `--debug`: Show debug information
- `--base-prompt`: Path to base prompt template (default: inputs/base_prompt.md)

The optimized resume will be saved to the `outputs` directory with a timestamp.

## API Endpoints

### Health Check
```
GET /api/v1/health
```
Returns API health status and version information.

### List Available Models
```
GET /api/v1/models
```
Lists available AI models for each provider.

Optional query parameter:
- `provider`: Filter models by specific provider

### Optimize Resume
```
POST /api/v1/optimize
```
Optimizes a resume based on provided content and parameters.

Request body:
```json
{
    "resume_content": "string",
    "guidelines": "string (optional)",
    "custom_prompt": "string (optional)",
    "ai_provider": "string (optional)",
    "model": "string (optional)"
}
```

## Notes

- The demo tool requires both the resume optimizer server (port 5000) and document converter server (port 5001)
- Maximum resume content length is 15000 characters
- Supported AI providers: Mistral, OpenAI, Anthropic, DeepSeek
- Default configuration uses Mistral as the AI provider with 'mistral-large-latest' model
- Uses `uv` for faster Python package management and virtual environment handling
