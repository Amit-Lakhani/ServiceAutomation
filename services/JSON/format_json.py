from flask import Blueprint, request
import json

format_json_bp = Blueprint("format_json", __name__)

format_json_config = {
    "name": "Format JSON",
    "endpoint": "/api/format-json",
    "fields": [
        {
            "type": "textarea",
            "name": "format_json",
            "label": "Enter JSON",
            "required": True
        }
    ],
    "response": {
        "type": "text"
    }
}

@format_json_bp.route("/api/format-json", methods=["POST"])
def format_json():
    try:
        raw_json = request.form.get("format_json", "")
        parsed = json.loads(raw_json)  # ✅ safe parsing
        pretty = json.dumps(parsed, indent=4)
        return pretty, 200, {'Content-Type': 'text/plain'}
    except json.JSONDecodeError as e:
        return f"Invalid JSON input. Error: {str(e)}", 400
