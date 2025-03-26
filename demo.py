import argparse
import json
import subprocess
import sys
import time
import requests
from pathlib import Path
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()
DEFAULT_MODEL = os.getenv('MISTRAL_DEFAULT_MODEL', 'mistral-large-latest')

# Python interpreter paths for virtual environments
RESUME_OPTIMIZER_VENV = Path(__file__).parent / ".venv" / "Scripts" / "python.exe"
DOC2TEXT_VENV = Path(__file__).parent.parent / "doc2text" / ".venv" / "Scripts" / "python.exe"

def read_file_content(file_path):
    """Read content from a file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def wait_for_server(port=5000, timeout=10):
    """Wait for server to start."""
    url = f"http://localhost:{port}/api/v1/health"
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.ConnectionError:
            time.sleep(0.5)
    return False

def convert_document_to_text(file_path, port=5001):
    """Convert document to text using doc2text API."""
    url = f"http://localhost:{port}/api/v1/convert"
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(url, files=files)
    return response.json()['data']['text']

def optimize_resume(resume_content, guidelines=None, job_description=None, custom_prompt=None,
                     provider="mistral", model=None, debug=False, base_prompt_path=None):
    """Send optimization request to API."""
    url = "http://localhost:5000/api/v1/optimize"
    
    payload = {
        "resume_content": resume_content,
        "ai_provider": provider,
        "model": model or DEFAULT_MODEL
    }
    
    if guidelines:
        payload["guidelines"] = guidelines
    if job_description:
        payload["job_description"] = job_description
    if custom_prompt:
        payload["custom_prompt"] = custom_prompt
    if base_prompt_path:
        payload["base_prompt_path"] = base_prompt_path
        
    if debug:
        print("\nRequest Payload:")
        print(json.dumps(payload, indent=2))
        
    response = requests.post(url, json=payload)
    response_json = response.json()
    
    # Save output to file with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = Path('outputs') / f"output_{timestamp}.txt"
    
    with output_file.open("w", encoding="utf-8") as f:
        f.write(response_json["optimized_content"])
    
    if debug:
        print("\nResponse:")
        print(json.dumps(response_json, indent=2))
    else:
        print("\nOptimized Resume:")
        print(response_json["optimized_content"])
        
    print(f"\nOutput saved to: {output_file.relative_to(Path.cwd())}")

def main():
    parser = argparse.ArgumentParser(description="Resume Optimization Demo")
    parser.add_argument("--resume", required=True, help="Path to resume content file")
    parser.add_argument("--guidelines", default="inputs/RESUME_GUIDELINES.md",
                        help="Path to guidelines file")
    parser.add_argument("--model", help="Specific Mistral model to use")
    parser.add_argument("--custom-prompt", help="Additional instructions for optimization")
    parser.add_argument("--job-description", help="Path to job description file")
    parser.add_argument("--debug", action="store_true", help="Show debug information")
    parser.add_argument("--base-prompt", default="inputs/base_prompt.md",
                        help="Path to base prompt template")
    
    args = parser.parse_args()
    
    # Verify Python interpreter paths exist
    if not RESUME_OPTIMIZER_VENV.exists():
        print(f"Error: Resume optimizer venv not found at {RESUME_OPTIMIZER_VENV}")
        sys.exit(1)
    if not DOC2TEXT_VENV.exists():
        print(f"Error: Doc2text venv not found at {DOC2TEXT_VENV}")
        sys.exit(1)

    # Start doc2text server on port 5001
    doc2text_server = subprocess.Popen([
        str(DOC2TEXT_VENV),
        "-m", "flask",
        "--app", "app.api.document_converter",
        "run",
        "--port", "5001"
    ],
        cwd="../doc2text",
        stdout=subprocess.PIPE if not args.debug else None,
        stderr=subprocess.PIPE if not args.debug else None
    )

    # Start resume optimizer server on port 5000
    optimizer_server = subprocess.Popen([
        str(RESUME_OPTIMIZER_VENV),
        "app.py"
    ],
        stdout=subprocess.PIPE if not args.debug else None,
        stderr=subprocess.PIPE if not args.debug else None
    )
    
    # Wait for both servers to start
    servers_ready = wait_for_server(port=5001, timeout=10) and wait_for_server(port=5000, timeout=10)
    
    if not servers_ready:
        print("Error: One or both servers failed to start")
        doc2text_server.terminate()
        optimizer_server.terminate()
        sys.exit(1)
        
    try:
        # First convert document to text
        resume_text = convert_document_to_text(args.resume, port=5001)
        
        # Read guidelines and job description if provided
        guidelines = read_file_content(args.guidelines) if args.guidelines else None
        job_description = read_file_content(args.job_description) if args.job_description else None
        
        # Make optimization request
        optimize_resume(
            resume_content=resume_text,
            guidelines=guidelines,
            job_description=job_description,
            custom_prompt=args.custom_prompt,
            model=args.model,
            debug=args.debug,
            base_prompt_path=args.base_prompt
        )
    finally:
        doc2text_server.terminate()
        optimizer_server.terminate()

if __name__ == "__main__":
    main()