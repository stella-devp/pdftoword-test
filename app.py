from flask import Flask, request, send_file, make_response
from pdf2docx import Converter
import tempfile
import os
import logging
import traceback
import time
import fitz  # PyMuPDF for PDF text extraction

# Set up logging
log_dir = "/tmp/azure_app_logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(log_dir, "app.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Constants
STATIC_AUTH_TOKEN = "Wissda_101"
app = Flask(__name__)
TEMP_DIR = "/tmp"

# Function to extract text from PDF (optional, debug only)
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text += page.get_text("text")
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
    return text

@app.route('/convert', methods=['POST'])
def convert_pdf_to_docx():
    auth_token = request.headers.get('Authorization')
    if auth_token != STATIC_AUTH_TOKEN:
        logger.warning("Unauthorized access attempt")
        return {"error": "Unauthorized access. Invalid or missing token."}, 403

    timestamp = str(int(time.time()))
    pdf_temp_path = os.path.join(TEMP_DIR, f"input_{timestamp}.pdf")
    docx_temp_path = os.path.join(TEMP_DIR, f"output_{timestamp}.docx")

    try:
        # Save input PDF
        if 'file' in request.files:
            file = request.files['file']
            file.save(pdf_temp_path)
            logger.info(f"Received file: {file.filename}")
        else:
            with open(pdf_temp_path, 'wb') as f:
                f.write(request.data)
            logger.info("Received binary data")

        # Debug text extract (optional)
        if app.debug:
            logger.info("Extracting text from PDF...")
            extracted = extract_text_from_pdf(pdf_temp_path)
            logger.info(f"Extracted text preview: {extracted[:500]}")

        # Convert PDF → DOCX
        logger.info("Starting conversion...")
        cv = Converter(pdf_temp_path)
        try:
            cv.convert(docx_temp_path, start=0, end=None)
        finally:
            cv.close()

        # Prepare response
        response = make_response(send_file(
            docx_temp_path,
            as_attachment=True,
            download_name="converted.docx",
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ))
        response.headers["Content-Disposition"] = "attachment; filename=converted.docx"
        return response

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        logger.error(traceback.format_exc())
        return {"error": f"Conversion error: {str(e)}"}, 500

    finally:
        # Clean up
        for path in [pdf_temp_path, docx_temp_path]:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    logger.info(f"Deleted temp file: {path}")
            except Exception as e:
                logger.error(f"Failed to delete {path}: {str(e)}")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
