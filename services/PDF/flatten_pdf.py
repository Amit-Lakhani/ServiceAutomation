# flatten_pdf.py

from flask import Blueprint, request, send_file
from PyPDF2 import PdfReader, PdfWriter
import os
from werkzeug.utils import secure_filename

flatten_pdf_bp = Blueprint("flatten_pdf", __name__)

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

flatten_pdf_config = {
    "name": "Flatten PDF",
    "endpoint": "/api/flatten-pdf",
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

@flatten_pdf_bp.route("/api/flatten-pdf", methods=["POST"])
def flatten_pdf():
    file = request.files.get("pdf_file")
    if not file:
        return "No PDF file uploaded", 400

    filename = secure_filename(file.filename)
    base_name = os.path.splitext(filename)[0]

    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(RESULT_FOLDER, f"{base_name}_flattened.pdf")

    file.save(input_path)

    reader = PdfReader(input_path)
    writer = PdfWriter()

    # Copy pages while removing form fields and annotations
    for page in reader.pages:
        # Remove annotations (including form fields)
        if "/Annots" in page:
            page.__delitem__("/Annots")

        writer.add_page(page)

    # Remove the AcroForm entry to remove form fields
    if "/AcroForm" in reader.trailer["/Root"]:
        del reader.trailer["/Root"]["/AcroForm"]

    with open(output_path, "wb") as out_f:
        writer.write(out_f)

    # Optional cleanup
    os.remove(input_path)

    return send_file(
        output_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=os.path.basename(output_path)
    )
