from flask import Blueprint, request, send_file
from PyPDF2 import PdfReader, PdfWriter
import os
from werkzeug.utils import secure_filename
import io

decrypt_pdf_bp = Blueprint("decrypt_pdf", __name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

decrypt_pdf_config = {
    "name": "Decrypt PDF",
    "endpoint": "/api/decrypt_pdf",
    "fields": [
        {
            "type": "file",
            "name": "pdf_file",
            "label": "Upload Encrypted PDF",
            "required": True
        },
        {
            "type": "text",
            "name": "password",
            "label": "Password",
            "required": True
        }
    ],
    "response": {
        "type": "file"
    }
}

@decrypt_pdf_bp.route("/api/decrypt_pdf", methods=["POST"])
def decrypt_pdf():
    file = request.files.get("pdf_file")
    password = request.form.get("password")

    if not file:
        return "No PDF file uploaded", 400
    if not password:
        return "Password is required", 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    try:
        reader = PdfReader(input_path)
        if not reader.is_encrypted:
            os.remove(input_path)
            return "PDF is not encrypted", 400

        if not reader.decrypt(password):
            os.remove(input_path)
            return "Incorrect password", 401

        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)

        decrypted_filename = filename.rsplit('.', 1)[0] + "_decrypted.pdf"

    except Exception as e:
        os.remove(input_path)
        return f"Decryption failed: {str(e)}", 500

    os.remove(input_path)

    return send_file(
        output_stream,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=decrypted_filename
    )
