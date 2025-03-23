import os
import uuid
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
from PIL import Image
import pytesseract

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# تأكد من وجود المجلدات
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# مسار Tesseract المناسب لويندوز
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    extracted_text = ""
    original_filename = None
    reviews = [
        {"name": "ليلى من السعودية", "comment": "المنصة رائعة وسهلة جدًا، أنقذتني في مشروع التخرج!"},
        {"name": "أحمد من مصر", "comment": "أفضل أداة لتحويل ملفات PDF إلى نص عربي بدقة عالية."},
        {"name": "فاطمة من الإمارات", "comment": "جربت أدوات كثيرة، لكن هذه الأدق في النصوص العربية."},
        {"name": "زيد من الأردن", "comment": "أنصح بها لجميع المعلمين والمعلمات!"},
        {"name": "أمينة من الجزائر", "comment": "تعامل رائع وواجهة مريحة جدًا."},
        {"name": "عبدالله من الكويت", "comment": "أداة ممتازة ومجانية تمامًا!"},
        {"name": "رنا من قطر", "comment": "سريعة وسهلة وأنيقة 👌"},
        {"name": "يوسف من البحرين", "comment": "تحويل النصوص كان دقيق ومميز جدًا."},
        {"name": "هند من المغرب", "comment": "تصميم المنصة جذاب وسهل."},
        {"name": "سامي من تونس", "comment": "واجهة ممتازة وجودة OCR مذهلة."},
    ]

    if request.method == 'POST':
        file = request.files.get('file')
        lang = request.form.get('lang', 'ara+eng')

        if not file or file.filename == '':
            return render_template('index.html', text="❌ لم يتم اختيار أي ملف.", original_name=None, reviews=reviews)

        original_filename = file.filename

        if '.' not in original_filename:
            return render_template('index.html', text="❌ امتداد الملف غير معروف أو غير مدعوم.", original_name=original_filename, reviews=reviews)

        ext = original_filename.rsplit('.', 1)[1].lower()

        if ext not in ALLOWED_EXTENSIONS:
            return render_template('index.html', text="❌ نوع الملف غير مدعوم. الرجاء رفع PDF أو صورة (JPG/PNG).", original_name=original_filename, reviews=reviews)

        # توليد اسم ملف فريد
        filename = f"{uuid.uuid4().hex}.{ext}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            if ext == 'pdf':
                images = convert_from_path(filepath)
            else:
                images = [Image.open(filepath)]

            for image in images:
                text = pytesseract.image_to_string(image, lang=lang)
                extracted_text += text + '\n'

            output_path = os.path.join(OUTPUT_FOLDER, filename.rsplit('.', 1)[0] + '.txt')
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(extracted_text)

            return render_template('index.html', text=extracted_text, download_link=output_path, original_name=original_filename, reviews=reviews)

        except Exception as e:
            return render_template('index.html', text=f'⚠️ حدث خطأ أثناء المعالجة: {str(e)}', original_name=original_filename, reviews=reviews)

    return render_template('index.html', text=None, original_name=None, reviews=reviews)

@app.route('/download/<path:filename>')
def download_file(filename):
    return send_file(filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
