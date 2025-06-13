from flask import Flask, request, send_file, jsonify
from pdf2docx import Converter
import tempfile
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)  # This will log messages with level INFO or higher
logger = logging.getLogger(__name__)

# Define static token (you can store this in environment variables for better security)
STATIC_AUTH_TOKEN = "Wissda_ServiceNow_889"  # Replace this with your actual token

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_pdf_to_docx():
    # Step 1: Validate Authentication Token
    auth_token = request.headers.get('Authorization')
    
    if auth_token != STATIC_AUTH_TOKEN:
        logger.warning("Unauthorized access attempt")
        return jsonify({"error": "Unauthorized access. Invalid or missing token."}), 403

    try:
        # Step 2: Create temporary files
        pdf_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        docx_temp = tempfile.NamedTemporaryFile(delete=False, suffix='.docx')

        # Step 3: Handle file from ServiceNow
        if 'file' in request.files:
            file = request.files['file']
            file.save(pdf_temp.name)
            logger.info(f"Received file: {file.filename}")
        else:
            # For application/pdf content-type (binary stream)
            pdf_temp.write(request.data)
            pdf_temp.flush()
            logger.info("Received binary data")

        # Step 4: Convert PDF → DOCX
        logger.info("Starting conversion...")
        cv = Converter(pdf_temp.name)
        cv.convert(docx_temp.name, start=0, end=None)
        cv.close()

        # Step 5: Return DOCX file as response
        logger.info("Conversion successful, sending DOCX...")
        return send_file(
            docx_temp.name,
            as_attachment=True,
            download_name="converted.docx",
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
    
    except ZeroDivisionError as e:
        logger.error(f"ZeroDivisionError occurred: {str(e)}")
        return f"❌ Conversion error: Division by zero error. Please check the input data.", 500
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return f"❌ Conversion error: {str(e)}", 500

    finally:
        # Cleanup temp files
        if os.path.exists(pdf_temp.name):
            os.remove(pdf_temp.name)
            logger.info(f"Deleted temporary PDF file: {pdf_temp.name}")
        if os.path.exists(docx_temp.name):
            os.remove(docx_temp.name)
            logger.info(f"Deleted temporary DOCX file: {docx_temp.name}")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
