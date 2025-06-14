import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import re
import arabic_reshaper
from bidi.algorithm import get_display
import os

# ✅ تأكد من المسار الصحيح لـ Tesseract
pytesseract.pytesseract.tesseract_cmd = r"c:\Program Files\Tesseract-OCR\tesseract.exe"

def fix_mixed_lines(text):
    """
    معالجة النص سطرًا سطرًا لإصلاح اتجاه الأسطر التي تحتوي على العربية فقط.
    """
    lines = text.splitlines()
    fixed_lines = []
    for line in lines:
        # إزالة المسافات الزائدة
        line = line.strip()
        if not line:
            continue
        # إذا فيه حروف عربية → reshape + bidi
        if re.search(r'[\u0600-\u06FF]', line):
            reshaped = arabic_reshaper.reshape(line)
            fixed = get_display(reshaped)
            fixed_lines.append(fixed)
        else:
            fixed_lines.append(line)
    return '\n'.join(fixed_lines)

def ocr_pdf(pdf_path, dpi=300):
    """
    قراءة PDF صفحة بصفحة وتحويله إلى نص باستخدام Tesseract.
    """
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"❌ الملف غير موجود: {pdf_path}")

    doc = fitz.open(pdf_path)
    all_text = []

    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        pix = page.get_pixmap(dpi=dpi)
        img = Image.open(io.BytesIO(pix.tobytes("png")))
        
        # استخدام Tesseract
        raw_text = pytesseract.image_to_string(img, lang="ara+eng")

        # تصحيح الاتجاه للأسطر
       # final_text = fix_mixed_lines(raw_text)

        all_text.append(f"\n--- Page {page_number + 1} ---\n{raw_text}")

    return '\n'.join(all_text)

def save_text_to_file(text, output_path="output.txt"):
    """
    حفظ النص الناتج إلى ملف نصي.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"✅ تم حفظ النص هنا: {output_path}")

if __name__ == "__main__":
    # 👇 ضع مسار الـ PDF الخاص بك هنا
    pdf_path = r"c:\Users\Mahmoud\Desktop\PDF_py\file3.pdf"

    try:
        result_text = ocr_pdf(pdf_path)
        print(result_text)

        # 👇 حفظ الملف تلقائيًا
        save_text_to_file(result_text, "output.txt")

    except Exception as e:
        print(f"❌ حدث خطأ: {e}")
