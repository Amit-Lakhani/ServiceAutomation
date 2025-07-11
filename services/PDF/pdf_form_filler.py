# pdf_form_filler.py

from flask import Blueprint, request, send_file
from werkzeug.utils import secure_filename
import os
import io
from pdfrw import PdfReader, PdfWriter, PdfDict, PdfName

pdf_form_filler_bp = Blueprint("pdf_form_filler", __name__)

UPLOAD_FOLDER = "uploads"
RESULT_FOLDER = "results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

pdf_form_filler_config = {
    "name": "PDF Form Filler",
    "endpoint": "/api/pdf_form_filler",
    "fields": [
        {
            "type": "file",
            "name": "pdf_file",
            "label": "Upload PDF Form",
            "required": True
        },
        {
            "type": "textarea",
            "name": "form_data",
            "label": "Form Data (JSON)",
            "required": True
        }
    ],
    "response": {
        "type": "file"
    }
}

def fill_pdf(input_pdf_path, data_dict, output_pdf_path):
    template_pdf = PdfReader(input_pdf_path)
    annotations = template_pdf.pages[0]['/Annots']

    if annotations is None:
        raise ValueError("No form fields found in PDF.")

    for annotation in annotations:
        if annotation['/Subtype'] == PdfName('Widget') and annotation.get('/T'):
            key = annotation['/T'][1:-1]  # Strip parentheses
            if key in data_dict:
                annotation.update(
                    PdfDict(V='{}'.format(data_dict[key]))
                )
                annotation.update(PdfDict(AP=''))
    PdfWriter().write(output_pdf_path, template_pdf)

@pdf_form_filler_bp.route("/api/pdf_form_filler", methods=["POST"])
def pdf_form_filler():
    file = request.files.get("pdf_file")
    form_data = request.form.get("form_data")

    if not file:
        return "No PDF file uploaded", 400
    if not form_data:
        return "No form data provided", 400

    import json
    try:
        data_dict = json.loads(form_data)
    except Exception:
        return "Invalid JSON in form data", 400

    filename = secure_filename(file.filename)
    base_name = os.path.splitext(filename)[0]

    input_path = os.path.join(UPLOAD_FOLDER, filename)
    output_path = os.path.join(RESULT_FOLDER, f"{base_name}_filled.pdf")

    file.save(input_path)

    try:
        fill_pdf(input_path, data_dict, output_path)
    except Exception as e:
        os.remove(input_path)
        return f"Failed to fill PDF form: {str(e)}", 500

    os.remove(input_path)

    return send_file(
        output_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=os.path.basename(output_path)
    )
