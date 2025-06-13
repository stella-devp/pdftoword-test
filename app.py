from flask import Flask, request, send_file
from pdf2docx import Converter
import tempfile
import os

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_pdf_to_docx():
    try:
        # Step 1: Create temporary files
        pdf_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        docx_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')

        # Step 2: Handle file from ServiceNow
        if 'file' in request.files:
            file = request.files['file']
            file.save(pdf_temp.name)
        else:
            # For application/pdf content-type (binary stream)
            pdf_temp.write(request.data)
            pdf_temp.flush()

        # Step 3: Convert PDF → DOCX
        cv = Converter(pdf_temp.name)
        cv.convert(docx_temp.name, start=0, end=None)
        cv.close()

        # Step 4: Return DOCX file as response
        return send_file(
            docx_temp.name,
            as_attachment=True,
            download_name="converted.docx",
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    except Exception as e:
        return f"❌ Conversion error: {str(e)}", 500
    finally:
        # Cleanup temp files
        if os.path.exists(pdf_temp.name):
            os.remove(pdf_temp.name)
        if os.path.exists(docx_temp.name):
            os.remove(docx_temp.name)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
