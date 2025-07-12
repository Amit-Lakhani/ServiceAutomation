from flask import Blueprint, request, send_file
from PyPDF2 import PdfReader, PdfWriter
import os
from werkzeug.utils import secure_filename
import io

compress_pdf_bp = Blueprint("compress_pdf", __name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

compress_pdf_config = {
    "name": "Compress PDF",
    "endpoint": "/api/compress-pdf",
    "fields": [
        {
            "type": "file",
            "name": "compress_pdf",
            "label": "Upload PDF",
            "required": True
        }
    ],
    "response": {
        "type": "file"
    }
}

@compress_pdf_bp.route("/api/compress-pdf", methods=["POST"])
def compress_pdf():
    file = request.files.get("compress_pdf")
    if not file:
        return "No file uploaded", 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        writer.add_page(page)

    # Apply basic compression
    writer.add_metadata(reader.metadata)
    writer._header = b"%PDF-1.4"
    writer.compress_content_streams()

    output_stream = io.BytesIO()
    writer.write(output_stream)
    output_stream.seek(0)

    output_filename = os.path.splitext(filename)[0] + "_compressed.pdf"

    return send_file(
        output_stream,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=output_filename
    )
