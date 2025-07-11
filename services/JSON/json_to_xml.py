from flask import Blueprint, request, Response
import dicttoxml
import json

json_to_xml_bp = Blueprint("json_to_xml", __name__)

json_to_xml_config = {
    "name": "Convert JSON to XML",
    "endpoint": "/api/json_to_xml",
    "fields": [
        {
            "type": "textarea",
            "name": "json_to_xml",
            "label": "Enter JSON",
            "required": True
        }
    ],
    "response": {
        "type": "text"
    }
}

@json_to_xml_bp.route("/api/json_to_xml", methods=["POST"])
def json_to_xml():
    json_data = request.form.get("json_to_xml")
    if not json_data:
        return "Missing JSON input", 400

    try:
        data_dict = json.loads(json_data)
    except json.JSONDecodeError:
        return "Invalid JSON", 400

    xml_bytes = dicttoxml.dicttoxml(data_dict, custom_root='root', attr_type=False)
    xml_str = xml_bytes.decode()

    return Response(xml_str, mimetype='application/xml')
