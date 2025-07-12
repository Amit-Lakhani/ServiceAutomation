from flask import Blueprint, request, send_file
from PyPDF2 import PdfMerger
import os
from werkzeug.utils import secure_filename

merge_pdf_bp = Blueprint("merge_pdf", __name__)

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

merge_pdf_config = {
    "name": "Merge PDF",
    "endpoint": "/api/merge-pdf",
    "fields": [
        {
            "type": "file",
            "name": "merge_pdf",
            "label": "Select PDFs to Merge",
            "required": True,
            "multiple": True
        }
    ],
    "response": {
        "type": "file"
    }
}

@merge_pdf_bp.route("/api/merge-pdf", methods=["POST"])
def merge_pdf():
    files = request.files.getlist("merge_pdf")
    if not files:
        return "No PDF files uploaded", 400

    merger = PdfMerger()
    filenames = []

    for f in files:
        filename = secure_filename(f.filename)
        path = os.path.join(UPLOAD_FOLDER, filename)
        f.save(path)
        filenames.append(path)
        merger.append(path)

    output_path = os.path.join(RESULT_FOLDER, "merged_output.pdf")
    merger.write(output_path)
    merger.close()

    # Optional cleanup of uploaded files after merge
    for path in filenames:
        os.remove(path)

    return send_file(output_path, as_attachment=True, download_name="merged_output.pdf")
