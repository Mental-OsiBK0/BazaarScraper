Market Okuyucu

Oyundaki market ekranından ürün isimlerini okuyor. Pillow ile görüntüyü düzeltip Tesseract OCR ile okuyor.

pip install pillow pytesseract pyautogui
python main.py resim.png
python main.py --ekran --bolge 100 200 600 700

Bölge koordinatlarını konum.py ile bulabilirsin. Tesseract ve Türkçe dil paketi kurulu olmalı.
