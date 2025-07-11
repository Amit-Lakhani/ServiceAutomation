from flask import Blueprint, request, send_file
from PyPDF2 import PdfReader, PdfWriter
import os
from werkzeug.utils import secure_filename
import zipfile
import io

split_pdf_bp = Blueprint("split_pdf", __name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

split_pdf_config = {
    "name": "Split PDF",
    "endpoint": "/api/split_pdf",
    "fields": [
        {
            "type": "file",
            "name": "split_pdf",
            "label": "Upload PDF",
            "required": True
        }
    ],
    "response": {
        "type": "file"
    }
}

@split_pdf_bp.route("/api/split_pdf", methods=["POST"])
def split_pdf():
    file = request.files.get("split_pdf")
    if not file:
        return "No file uploaded", 400

    filename = secure_filename(file.filename)
    base_name = os.path.splitext(filename)[0]
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    reader = PdfReader(input_path)

    # Prepare ZIP archive in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)

            output_stream = io.BytesIO()
            writer.write(output_stream)
            output_stream.seek(0)

            part_filename = f"{base_name}_page_{i+1}.pdf"
            zipf.writestr(part_filename, output_stream.read())

    zip_buffer.seek(0)
    zip_filename = f"{base_name}_split_pages.zip"

    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name=zip_filename
    )
