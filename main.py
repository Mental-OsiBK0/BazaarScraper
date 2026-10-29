# Oyundaki market ekranından belli renkteki isimleri okuyup ekrandaki konumlarını buluyor
# python main.py pazar.png
# python main.py --ekran --bolge 100 200 600 700  (koordinatlar konum.py ile)

import argparse
import sys

import cv2
import numpy as np
import pytesseract
from PIL import ImageGrab

RENK = "FFFF80"  # marketteki isimlerin rengi
BUYUTME = 2


def hex_to_bgr(hex_renk):
    hex_renk = hex_renk.lstrip("#")
    r, g, b = (int(hex_renk[i:i + 2], 16) for i in (0, 2, 4))
    return np.array([b, g, r])


def renk_maskele(image, hex_renk, tolerans):
    # sadece aradığımız renge yakın pikseller kalsın
    renk = hex_to_bgr(hex_renk)
    alt = np.clip(renk - tolerans, 0, 255).astype(np.uint8)
    ust = np.clip(renk + tolerans, 0, 255).astype(np.uint8)
    maske = cv2.inRange(image, alt, ust)

    # tesseract beyaz zemin siyah yazıyı daha iyi okuyor
    sonuc = cv2.bitwise_not(maske)
    return cv2.resize(sonuc, None, fx=BUYUTME, fy=BUYUTME, interpolation=cv2.INTER_CUBIC)


def kelimeleri_bul(image, dil, offset):
    # image_to_boxes harf harf veriyordu, image_to_data kelime kelime veriyor
    veri = pytesseract.image_to_data(image, lang=dil, config="--psm 6",
                                     output_type=pytesseract.Output.DICT)
    kelimeler = []
    for i, metin in enumerate(veri["text"]):
        metin = metin.strip()
        if len(metin) < 2 or float(veri["conf"][i]) < 30:
            continue
        # büyütmeyi geri al, bölge kesildiyse ekran koordinatına çevir
        x = (veri["left"][i] + veri["width"][i] // 2) // BUYUTME + offset[0]
        y = (veri["top"][i] + veri["height"][i] // 2) // BUYUTME + offset[1]
        kelimeler.append((metin, x, y))
    return kelimeler


def goruntu_al(dosya, ekran, bolge):
    if ekran:
        ss = ImageGrab.grab(bbox=tuple(bolge) if bolge else None)
        return cv2.cvtColor(np.array(ss), cv2.COLOR_RGB2BGR)
    image = cv2.imread(dosya)
    if image is None:
        sys.exit(f"{dosya} açılamadı")
    if bolge:
        x1, y1, x2, y2 = bolge
        image = image[y1:y2, x1:x2]
    return image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dosya", nargs="?")
    parser.add_argument("--ekran", action="store_true", help="dosya yerine ekranı oku")
    parser.add_argument("--bolge", type=int, nargs=4, metavar=("X1", "Y1", "X2", "Y2"))
    parser.add_argument("--renk", default=RENK, help="aranan yazı rengi, örn FFFF80")
    parser.add_argument("--tolerans", type=int, default=40)
    parser.add_argument("--dil", default="tur")
    parser.add_argument("--maske", help="ara görüntüyü kaydet, ayar yaparken işe yarıyor")
    parser.add_argument("-o", "--cikti", help="sonuçları txt'ye yaz")
    args = parser.parse_args()

    if not args.dosya and not args.ekran:
        parser.error("resim ver ya da --ekran kullan")
    if args.bolge and (args.bolge[2] <= args.bolge[0] or args.bolge[3] <= args.bolge[1]):
        parser.error("bölge koordinatları ters")
    try:
        if args.dil not in pytesseract.get_languages():
            sys.exit(f"'{args.dil}' dil paketi yok")
    except pytesseract.TesseractNotFoundError:
        sys.exit("Tesseract kurulu değil")

    image = goruntu_al(args.dosya, args.ekran, args.bolge)
    islenmis = renk_maskele(image, args.renk, args.tolerans)
    if args.maske:
        cv2.imwrite(args.maske, islenmis)

    offset = args.bolge[:2] if args.bolge else (0, 0)
    kelimeler = kelimeleri_bul(islenmis, args.dil, offset)

    print(f"{len(kelimeler)} isim bulundu\n")
    for metin, x, y in kelimeler:
        print(f"{metin:<20} ({x}, {y})")

    if args.cikti:
        with open(args.cikti, "w", encoding="utf-8") as f:
            f.writelines(f"{m}\t{x}\t{y}\n" for m, x, y in kelimeler)
        print(f"\n{args.cikti} kaydedildi")


if __name__ == "__main__":
    main()
