# extract_text_from_pdf.py

from flask import Blueprint, request, jsonify
from PyPDF2 import PdfReader
import os
from werkzeug.utils import secure_filename

extract_text_bp = Blueprint("extract_text", __name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

extract_text_from_pdf_config = {
    "name": "Extract Text from PDF",
    "endpoint": "/api/extract-text",
    "fields": [
        {
            "type": "file",
            "name": "pdf_file",
            "label": "Upload PDF",
            "required": True
        }
    ],
    "response": {
        "type": "text"
    }
}

@extract_text_bp.route("/api/extract-text", methods=["POST"])
def extract_text():
    file = request.files.get("pdf_file")
    if not file:
        return "No PDF file uploaded", 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    try:
        reader = PdfReader(input_path)
        full_text = []
        for page in reader.pages:
            text = page.extract_text()
            if text:
                full_text.append(text)
        extracted_text = "\n\n".join(full_text)
    except Exception as e:
        os.remove(input_path)
        return f"Failed to extract text: {str(e)}", 500

    os.remove(input_path)
    return extracted_text
