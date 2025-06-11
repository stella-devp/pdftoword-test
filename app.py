from flask import Flask, request, send_file
from pdf2docx import Converter
import os, uuid

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_pdf():
    file = request.files.get('file')
    if not file:
        return {"error": "No PDF provided"}, 400

    temp_pdf = f"{uuid.uuid4()}.pdf"
    temp_docx = f"{uuid.uuid4()}.docx"

    try:
        file.save(temp_pdf)
        cv = Converter(temp_pdf)
        cv.convert(temp_docx)
        cv.close()

        return send_file(temp_docx, as_attachment=True)

    finally:
        if os.path.exists(temp_pdf): os.remove(temp_pdf)
        if os.path.exists(temp_docx): os.remove(temp_docx)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
