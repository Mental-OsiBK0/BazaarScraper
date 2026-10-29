# Market Okuyucu

Oyundaki market ekranından belli renkteki oyuncu isimlerini okuyup ekrandaki konumlarını buluyor. OpenCV ile sadece o renkteki yazıları ayırıyor, sonra Tesseract OCR ile okuyor.

```
pip install opencv-python pytesseract pillow pyautogui
python main.py resim.png
python main.py --ekran --bolge 100 200 600 700
```

Bölge koordinatlarını `konum.py` ile bulabilirsin. Farklı renkte yazılar için `--renk FFFF80` gibi hex kodu ver. Tesseract ve Türkçe dil paketi kurulu olmalı.
