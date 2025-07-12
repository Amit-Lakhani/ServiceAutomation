from flask import Blueprint, request, send_file
from werkzeug.utils import secure_filename
import os
import io
import zipfile
from PyPDF2 import PdfReader

download_image_bp = Blueprint("download_image", __name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

download_image_from_pdf_config = {
    "name": "Extract Images from PDF",
    "endpoint": "/api/extract-images",
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

def extract_images_from_pdf(reader, base_name):
    images = []
    counter = 1
    for page_num, page in enumerate(reader.pages, start=1):
        if "/XObject" in page["/Resources"]:
            xObject = page["/Resources"]["/XObject"].get_object()
            for obj_name in xObject:
                obj = xObject[obj_name]
                if obj["/Subtype"] == "/Image":
                    data = obj.get_data()
                    ext = None
                    if obj["/Filter"] == "/DCTDecode":
                        ext = "jpg"
                    elif obj["/Filter"] == "/JPXDecode":
                        ext = "jp2"
                    elif obj["/Filter"] == "/FlateDecode":
                        ext = "png"
                    else:
                        ext = "bin"  # fallback

                    img_name = f"{base_name}_images_{counter}.{ext}"
                    images.append((img_name, data))
                    counter += 1
    return images

@download_image_bp.route("/api/extract-images", methods=["POST"])
def extract_images():
    file = request.files.get("pdf_file")
    if not file:
        return "No PDF file uploaded", 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    try:
        reader = PdfReader(input_path)
        base_name = filename.rsplit(".", 1)[0]
        images = extract_images_from_pdf(reader, base_name)

        if not images:
            os.remove(input_path)
            return "No images found in PDF", 404

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for img_name, img_data in images:
                zipf.writestr(img_name, img_data)

        zip_buffer.seek(0)
        zip_filename = f"{base_name}_images.zip"
    except Exception as e:
        os.remove(input_path)
        return f"Failed to extract images: {str(e)}", 500

    os.remove(input_path)

    return send_file(
        zip_buffer,
        mimetype="application/zip",
        as_attachment=True,
        download_name=zip_filename,
    )
