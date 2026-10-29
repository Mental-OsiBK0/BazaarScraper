# Oyundaki market ekranından ürün isimlerini OCR ile okuyor
# python main.py resim.png
# python main.py --ekran --bolge 100 200 600 700  (koordinatlar konum.py ile)

import argparse
import sys

from PIL import Image, ImageEnhance, ImageFilter, ImageGrab, ImageOps, ImageStat
import pytesseract

DIL = "tur"


def kontrast(image):
    image = ImageEnhance.Contrast(image).enhance(2.0)
    return image.filter(ImageFilter.SHARPEN)


def buyut(image, oran=2):
    # küçük yazılarda büyütünce daha iyi okuyor
    return image.resize((image.width * oran, image.height * oran), Image.LANCZOS)


def esikleme(image, esik=150):
    image = ImageOps.grayscale(buyut(image))
    image = ImageEnhance.Contrast(image).enhance(2.0)
    image = image.point(lambda p: 255 if p > esik else 0)
    # arka plan koyuysa ters çevir, tesseract beyaz zemin siyah yazıyı seviyor
    if ImageStat.Stat(image).mean[0] < 128:
        image = ImageOps.invert(image)
    return image


YONTEMLER = {"kontrast": kontrast, "buyut": buyut, "esikleme": esikleme}


def dil_kontrol(dil):
    try:
        kurulu = pytesseract.get_languages()
    except pytesseract.TesseractNotFoundError:
        sys.exit("Tesseract kurulu değil")
    if dil not in kurulu:
        sys.exit(f"'{dil}' dil paketi yok, kurulu olanlar: {', '.join(kurulu)}")


def oku(image, dil=DIL):
    metin = pytesseract.image_to_string(image, lang=dil)
    satirlar = [s.strip() for s in metin.splitlines()]
    # boş satırları ve tek karakterlik çöpleri at
    return [s for s in satirlar if len(s) >= 2 and any(c.isalpha() for c in s)]


def goruntu_al(dosya, ekran, bolge):
    if ekran:
        return ImageGrab.grab(bbox=tuple(bolge) if bolge else None)
    try:
        image = Image.open(dosya)
    except FileNotFoundError:
        sys.exit(f"{dosya} bulunamadı")
    return image.crop(tuple(bolge)) if bolge else image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dosya", nargs="?")
    parser.add_argument("--ekran", action="store_true", help="dosya yerine ekranı oku")
    parser.add_argument("--yontem", choices=[*YONTEMLER, "hepsi"], default="esikleme")
    parser.add_argument("--bolge", type=int, nargs=4, metavar=("X1", "Y1", "X2", "Y2"))
    parser.add_argument("--dil", default=DIL)
    parser.add_argument("-o", "--cikti", help="sonuçları txt'ye yaz")
    args = parser.parse_args()

    if not args.dosya and not args.ekran:
        parser.error("resim ver ya da --ekran kullan")
    if args.bolge and (args.bolge[2] <= args.bolge[0] or args.bolge[3] <= args.bolge[1]):
        parser.error("bölge koordinatları ters")
    dil_kontrol(args.dil)

    image = goruntu_al(args.dosya, args.ekran, args.bolge)
    if args.yontem == "hepsi":
        secilenler = YONTEMLER
    else:
        secilenler = {args.yontem: YONTEMLER[args.yontem]}

    sonuc = []
    for ad, yontem in secilenler.items():
        urunler = oku(yontem(image), args.dil)
        print(f"\n[{ad}] {len(urunler)} satır")
        for urun in urunler:
            print("  -", urun)
        sonuc += [f"[{ad}]", *urunler, ""]

    if args.cikti:
        with open(args.cikti, "w", encoding="utf-8") as f:
            f.write("\n".join(sonuc))
        print(f"\n{args.cikti} kaydedildi")


if __name__ == "__main__":
    main()
    
