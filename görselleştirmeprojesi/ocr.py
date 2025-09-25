import pytesseract
from PIL import Image
import os
from pdf2image import convert_from_path

# Tesseract yolunu belirtin (Tesseract'ı kurduğunuz dizine göre değişir)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# OCR işlemi için dil ayarı (Türkçe için "tur")
ocr_language = "tur"

# Görsellerin ve PDF'lerin bulunduğu klasör
input_folder = r'C:\Users\Furkan\Desktop\görselleştirmeprojesi\ocr gorsel'

# Çıktıların kaydedileceği klasör
output_folder = r'C:\Users\Furkan\Desktop\görselleştirmeprojesi\ocr yazi'

# Tüm yazıları birleştirip bir dosyaya yazacağımız bir değişken
combined_text = ""

# Çıktı klasörünü kontrol et, yoksa oluştur
os.makedirs(output_folder, exist_ok=True)

# Poppler yolunu belirtin
poppler_path = r'C:\Poppler\Library\bin'

# Klasördeki tüm dosyaları işleme
for filename in os.listdir(input_folder):
    file_path = os.path.join(input_folder, filename)
    
    if filename.lower().endswith(('.png', '.jpg', '.jpeg')):  # Görsel dosyalarını filtrele
        # Görseli aç ve OCR işlemi yap
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img, lang=ocr_language)

        # Çıktı dosyasını oluştur
        output_file = os.path.join(output_folder, f'{os.path.splitext(filename)[0]}.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(text)

        # Her bir dosyanın içeriğini birleştir
        combined_text += f"--- {filename} (Görsel) ---\n{text.strip()}\n\n"
        
        print(f"{filename} (görsel) işlendi ve çıktı kaydedildi.")
    
    elif filename.lower().endswith('.pdf'):  # PDF dosyalarını filtrele
        try:
            # PDF dosyasını resimlere dönüştür
            pages = convert_from_path(file_path, 300, poppler_path=poppler_path)

            pdf_text = ""
            for page_num, page in enumerate(pages):
                # Her sayfayı OCR işlemiyle metne dönüştür
                page_text = pytesseract.image_to_string(page, lang=ocr_language)
                pdf_text += f"\n--- Sayfa {page_num + 1} ---\n{page_text.strip()}"

            # PDF çıktısı dosyasını oluştur
            output_file = os.path.join(output_folder, f'{os.path.splitext(filename)[0]}.txt')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(pdf_text)

            # PDF'nin tüm metnini birleştir
            combined_text += f"--- {filename} (PDF) ---\n{pdf_text.strip()}\n\n"
            
            print(f"{filename} (PDF) işlendi ve çıktı kaydedildi.")
        except Exception as e:
            print(f"{filename} (PDF) işlenirken hata oluştu: {e}")

# Tüm yazıları tek bir dosyada birleştir
combined_output_file = os.path.join(output_folder, 'toplubirlestirildi.txt')
with open(combined_output_file, 'w', encoding='utf-8') as f:
    f.write(combined_text.strip())

print("Tüm yazılar birleştirildi ve 'toplubirlestirildi.txt' dosyasına kaydedildi.")
