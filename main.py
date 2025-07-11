from flask import Flask, jsonify, render_template

# Import service modules as packages
from services.PDF import split_pdf, merge_pdf, compress_pdf, pdf_to_word, rotate_pdf, flatten_pdf, extract_text_from_pdf, download_image_from_pdf, encrypt_pdf, decrypt_pdf, pdf_form_filler
from services.JSON import json_to_xml, format_json

app = Flask(__name__)

# Register blueprints from each module
app.register_blueprint(split_pdf.split_pdf_bp)
app.register_blueprint(merge_pdf.merge_pdf_bp)
app.register_blueprint(compress_pdf.compress_pdf_bp)
app.register_blueprint(pdf_to_word.pdf_to_word_bp)
app.register_blueprint(rotate_pdf.rotate_pdf_bp)
app.register_blueprint(flatten_pdf.flatten_pdf_bp)
app.register_blueprint(extract_text_from_pdf.extract_text_bp)
app.register_blueprint(download_image_from_pdf.download_image_bp)
app.register_blueprint(encrypt_pdf.encrypt_pdf_bp)
app.register_blueprint(decrypt_pdf.decrypt_pdf_bp)
app.register_blueprint(pdf_form_filler.pdf_form_filler_bp)


app.register_blueprint(json_to_xml.json_to_xml_bp)
app.register_blueprint(format_json.format_json_bp)



# Collect all service configs from modules
all_service_configs = {
    "split_pdf": split_pdf.split_pdf_config,
    "merge_pdf": merge_pdf.merge_pdf_config,
    "compress_pdf": compress_pdf.compress_pdf_config,
    "rotate_pdf": rotate_pdf.rotate_pdf_config,
    "flatten_pdf": flatten_pdf.flatten_pdf_config,
    "extract_text_from_pdf": extract_text_from_pdf.extract_text_from_pdf_config,
    "download_image_from_pdf": download_image_from_pdf.download_image_from_pdf_config,
    "encrypt_pdf": encrypt_pdf.encrypt_pdf_config,
    "decrypt_pdf": decrypt_pdf.decrypt_pdf_config,
    "pdf_form_filler": pdf_form_filler.pdf_form_filler_config,
    "json_to_xml": json_to_xml.json_to_xml_config,
    "format_json": format_json.format_json_config,
    "pdf_to_word": pdf_to_word.pdf_to_word_config
}


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/service")
def service_page():
    return render_template("service.html")

@app.route("/api/services")
def get_services():
    return jsonify(all_service_configs)

if __name__ == "__main__":
    app.run(debug=True)
