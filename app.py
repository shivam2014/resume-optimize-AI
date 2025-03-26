from flask import Flask, request, jsonify
from config import Config
from ai_utils import AIProvider
from werkzeug.exceptions import BadRequest

app = Flask(__name__)
app.config.from_object(Config)

@app.errorhandler(Exception)
def handle_error(error):
    if isinstance(error, BadRequest):
        return jsonify({"error": str(error)}), 400
    
    app.logger.error(f"Unexpected error: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

@app.route("/api/v1/models", methods=["GET"])
def list_models():
    """List available AI providers and their models."""
    try:
        provider = request.args.get("provider")
        if provider:
            if provider not in Config.SUPPORTED_PROVIDERS:
                raise BadRequest(f"Unsupported AI provider: {provider}")
            return jsonify({
                "provider": provider,
                "models": Config.get_available_models(provider),
                "default_model": Config.get_default_model(provider)
            })
        
        return jsonify({
            "providers": {
                provider: {
                    "models": Config.get_available_models(provider),
                    "default_model": Config.get_default_model(provider)
                }
                for provider in Config.SUPPORTED_PROVIDERS
            }
        })

    except Exception as e:
        raise BadRequest(str(e))

@app.route("/api/v1/optimize", methods=["POST"])
def optimize_resume():
    try:
        data = request.get_json()
        
        if not data or "resume_content" not in data:
            raise BadRequest("Resume content is required")

        resume_content = data["resume_content"]
        if not resume_content or len(resume_content) > Config.MAX_INPUT_LENGTH:
            raise BadRequest(f"Resume content must be between 1 and {Config.MAX_INPUT_LENGTH} characters")

        # Optional parameters
        guidelines = data.get("guidelines")
        custom_prompt = data.get("custom_prompt")
        ai_provider = data.get("ai_provider", Config.DEFAULT_AI_PROVIDER)
        model = data.get("model")

        # Initialize AI provider and optimize resume
        try:
            optimizer = AIProvider(provider=ai_provider, model=model)
        except ValueError as e:
            raise BadRequest(str(e))

        optimized_content = optimizer(
            resume_content=resume_content,
            guidelines=guidelines,
            custom_prompt=custom_prompt
        )

        return jsonify({
            "status": "success",
            "optimized_content": optimized_content,
            "provider": ai_provider,
            "model": optimizer.get_current_model()
        })

    except Exception as e:
        raise BadRequest(str(e))

@app.route("/api/v1/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "version": "1.0.0"
    })

if __name__ == "__main__":
    app.run(debug=Config.DEBUG)