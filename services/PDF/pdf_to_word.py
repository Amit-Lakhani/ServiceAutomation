from flask import Blueprint, request, send_file
from werkzeug.utils import secure_filename
from pdf2docx import Converter
import os

pdf_to_word_bp = Blueprint("pdf_to_word", __name__)

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

pdf_to_word_config = {
    "name": "PDF to Word",
    "endpoint": "/api/pdf_to_word",
    "fields": [
        {
            "type": "file",
            "name": "pdf_file",
            "label": "Upload PDF",
            "required": True
        }
    ],
    "response": {
        "type": "file"
    }
}

@pdf_to_word_bp.route("/api/pdf_to_word", methods=["POST"])
def pdf_to_word():
    file = request.files.get("pdf_file")
    if not file:
        return "No PDF file uploaded", 400

    filename = secure_filename(file.filename)
    base_name = os.path.splitext(filename)[0]

    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(RESULT_FOLDER, f"{base_name}_converted.docx")

    file.save(input_path)

    try:
        cv = Converter(input_path)
        cv.convert(output_path)
        cv.close()
    except Exception as e:
        return f"Conversion failed: {str(e)}", 500

    # Optional cleanup of uploaded file after conversion
    os.remove(input_path)

    return send_file(
        output_path,
        mimetype="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        as_attachment=True,
        download_name=f"{base_name}.docx"
    )
