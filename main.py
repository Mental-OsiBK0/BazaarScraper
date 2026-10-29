"""
Oyun İçi Market Okuyucu
-----------------------
Oyun içi market ekran görüntülerinden ürün isimlerini OCR ile okur.
Görüntü, okuma doğruluğunu artırmak için Pillow ile ön işlemeden geçirilir.

Kullanım:
    python main.py pazar.png                  # varsayılan yöntemle oku
    python main.py pazar.png --yontem hepsi   # tüm yöntemleri karşılaştır
    python main.py --ekran                    # anlık ekran görüntüsünü oku
    python main.py pazar.png -o urunler.txt   # sonucu dosyaya kaydet
    python main.py --ekran --bolge 100 200 600 700   # ekranın sadece market alanını oku
"""

import argparse
import sys

from PIL import Image, ImageEnhance, ImageFilter, ImageGrab, ImageOps, ImageStat
import pytesseract

DIL = "tur"


# ---------- Ön işleme yöntemleri ----------

def kontrast_keskinlestir(image: Image.Image) -> Image.Image:
    """Kontrastı artırır ve görüntüyü keskinleştirir."""
    image = ImageEnhance.Contrast(image).enhance(2.0)
    return image.filter(ImageFilter.SHARPEN)


def buyut(image: Image.Image, oran: int = 2) -> Image.Image:
    """Küçük yazıların daha iyi okunması için görüntüyü büyütür."""
    return image.resize((image.width * oran, image.height * oran), Image.LANCZOS)


def gri_esikleme(image: Image.Image, esik: int = 150) -> Image.Image:
    """Büyütür, gri tona çevirir ve siyah-beyaz eşikleme uygular.
    Koyu arka planlı oyun arayüzlerinde genelde en iyi sonucu verir."""
    image = ImageOps.grayscale(buyut(image))
    image = ImageEnhance.Contrast(image).enhance(2.0)
    image = image.point(lambda p: 255 if p > esik else 0)
    # Açık renk yazı / koyu arka plan ise Tesseract için tersine çevir
    if ImageStat.Stat(image).mean[0] < 128:
        image = ImageOps.invert(image)
    return image


YONTEMLER = {
    "kontrast": kontrast_keskinlestir,
    "buyut": buyut,
    "esikleme": gri_esikleme,
}


# ---------- OCR ----------

def dil_kontrol(dil: str) -> None:
    """Tesseract ve istenen dil paketi kurulu mu, baştan kontrol eder."""
    try:
        kurulu = pytesseract.get_languages()
    except pytesseract.TesseractNotFoundError:
        sys.exit("Hata: Tesseract kurulu değil. https://github.com/tesseract-ocr/tesseract adresinden kurun.")
    if dil not in kurulu:
        sys.exit(f"Hata: '{dil}' dil paketi kurulu değil. Kurulu diller: {', '.join(kurulu)}\n"
                 f"'{dil}.traineddata' dosyasını https://github.com/tesseract-ocr/tessdata adresinden indirin.")


def metni_oku(image: Image.Image, dil: str = DIL) -> list[str]:
    """Görüntüdeki metni okur, boş ve anlamsız satırları ayıklar."""
    ham_metin = pytesseract.image_to_string(image, lang=dil)
    satirlar = [s.strip() for s in ham_metin.splitlines()]
    return [s for s in satirlar if len(s) >= 2 and any(c.isalpha() for c in s)]


def goruntu_al(dosya: str | None, ekran: bool, bolge: list[int] | None) -> Image.Image:
    """Dosyadan ya da ekrandan görüntü alır; bölge verilmişse sadece o alanı keser.
    Bölge koordinatları konum.py ile bulunabilir."""
    if ekran:
        return ImageGrab.grab(bbox=tuple(bolge) if bolge else None)
    try:
        image = Image.open(dosya)
    except FileNotFoundError:
        sys.exit(f"Hata: '{dosya}' bulunamadı.")
    return image.crop(tuple(bolge)) if bolge else image


# ---------- Ana program ----------

def main() -> None:
    parser = argparse.ArgumentParser(description="Oyun içi market ürün isimlerini OCR ile okur.")
    parser.add_argument("dosya", nargs="?", help="Okunacak ekran görüntüsü")
    parser.add_argument("--ekran", action="store_true", help="Dosya yerine anlık ekran görüntüsü al")
    parser.add_argument("--yontem", choices=[*YONTEMLER, "hepsi"], default="esikleme",
                        help="Ön işleme yöntemi (varsayılan: esikleme)")
    parser.add_argument("-o", "--cikti", help="Sonuçların kaydedileceği .txt dosyası")
    parser.add_argument("--dil", default=DIL, help="Tesseract dil kodu (varsayılan: tur)")
    parser.add_argument("--bolge", type=int, nargs=4, metavar=("X1", "Y1", "X2", "Y2"),
                        help="Sadece bu alanı oku: sol üst ve sağ alt köşe (konum.py ile bulun)")
    args = parser.parse_args()

    if not args.dosya and not args.ekran:
        parser.error("Bir görüntü dosyası verin ya da --ekran kullanın.")
    if args.bolge and (args.bolge[2] <= args.bolge[0] or args.bolge[3] <= args.bolge[1]):
        parser.error("--bolge: sağ alt köşe, sol üst köşenin sağında ve altında olmalı.")
    dil_kontrol(args.dil)

    image = goruntu_al(args.dosya, args.ekran, args.bolge)
    secilenler = YONTEMLER if args.yontem == "hepsi" else {args.yontem: YONTEMLER[args.yontem]}

    sonuc_metni = []
    for ad, yontem in secilenler.items():
        urunler = metni_oku(yontem(image), args.dil)
        baslik = f"[{ad}] {len(urunler)} satır bulundu"
        print(f"\n{baslik}\n" + "-" * len(baslik))
        for urun in urunler:
            print(f"  • {urun}")
        sonuc_metni += [baslik, *urunler, ""]

    if args.cikti:
        with open(args.cikti, "w", encoding="utf-8") as f:
            f.write("\n".join(sonuc_metni))
        print(f"\nSonuçlar '{args.cikti}' dosyasına kaydedildi.")


if __name__ == "__main__":
    main()
