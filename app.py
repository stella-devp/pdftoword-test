from flask import Flask, request, send_file, jsonify
from pdf2docx import Converter
import os, uuid

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert_pdf():
    try:
        file = request.files.get('file')
        if not file:
            return jsonify({"error": "No PDF file uploaded"}), 400

        temp_pdf = f"{uuid.uuid4()}.pdf"
        temp_docx = f"{uuid.uuid4()}.docx"
        file.save(temp_pdf)

        # 변환 시도
        cv = Converter(temp_pdf)
        cv.convert(temp_docx)
        cv.close()

        # 파일 존재 여부 체크 후 전송
        if os.path.exists(temp_docx):
            response = send_file(temp_docx, as_attachment=True)
        else:
            return jsonify({"error": "Conversion failed, no Word file created"}), 500

        return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # 삭제는 응답 후에 지연 시킬 수도 있음
        try:
            if os.path.exists(temp_pdf): os.remove(temp_pdf)
            if os.path.exists(temp_docx): os.remove(temp_docx)
        except:
            pass
