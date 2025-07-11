from flask import Blueprint, request, send_file
from PyPDF2 import PdfReader, PdfWriter
import os
from werkzeug.utils import secure_filename
import io

rotate_pdf_bp = Blueprint("rotate_pdf", __name__)

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

rotate_pdf_config = {
    "name": "Rotate PDF",
    "endpoint": "/api/rotate_pdf",
    "fields": [
        {
            "type": "file",
            "name": "pdf_file",
            "label": "Upload PDF",
            "required": True
        },
        {
            "type": "number",
            "name": "angle",
            "label": "Rotation Angle (degrees)",
            "required": True
        }
    ],
    "response": {
        "type": "file"
    }
}

@rotate_pdf_bp.route("/api/rotate_pdf", methods=["POST"])
def rotate_pdf():
    file = request.files.get("pdf_file")
    if not file:
        return "No PDF file uploaded", 400

    try:
        angle = int(request.form.get("angle", 0))
    except ValueError:
        return "Invalid rotation angle", 400

    if angle % 90 != 0:
        return "Angle must be a multiple of 90", 400

    filename = secure_filename(file.filename)
    base_name = os.path.splitext(filename)[0]

    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        page.rotate(angle)
        writer.add_page(page)

    output_filename = f"{base_name}_rotated.pdf"
    output_path = os.path.join(RESULT_FOLDER, output_filename)

    with open(output_path, "wb") as f_out:
        writer.write(f_out)

    os.remove(input_path)  # Clean up uploaded file

    return send_file(
        output_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=output_filename
    )
