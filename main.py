from PIL import Image, ImageEnhance, ImageFilter, ImageFont, ImageDraw
import pytesseract

# Görüntüyü açın

def yontem_1():
    image = Image.open('pazar_png.png')

    # Görüntüyü iyileştirin
    enhancer = ImageEnhance.Contrast(image)
    enhanced_image = enhancer.enhance(2.0)  # Kontrastı artır
    enhanced_image = enhanced_image.filter(ImageFilter.SHARPEN)  # Keskinleştir

    # İyileştirilmiş görüntüden metini çıkarın
    text = pytesseract.image_to_string(enhanced_image, lang='tur')

    print(text)

def yontem_2():

    # Görüntüyü açın
    image = Image.open('pazar_png.png')

    # Görüntüyü büyütün
    bigger_image = image.resize((image.width * 2, image.height * 2))

    # Büyütülmüş görüntüden metni çıkarın
    text = pytesseract.image_to_string(bigger_image, lang='tur')

    print(text)

def yontem_3():

    # Görüntüyü açın
    image = Image.open('pazar_png.png')

    # Görüntüyü büyütün
    bigger_image = image.resize((image.width * 2, image.height * 2))

    # Farklı bir yazı tipi ve boyutu seçin
    font = ImageFont.load_default()  # Varsayılan bir yazı tipi ve boyutu kullanabilirsiniz

    # Metin çizmek için bir çizim nesnesi oluşturun
    draw = ImageDraw.Draw(bigger_image)

    # Görüntünün üst kısmına metni ekleyin
    text = pytesseract.image_to_string(bigger_image, lang='tur')
    text = text.encode('utf-8').decode('latin-1')

    draw.text((20, 20), text, fill="white", font=font)  # Metni görüntüye çizin


    # Metni görüntüden çıkarın
    text = pytesseract.image_to_string(bigger_image, lang='tur')

    print(text)

yontem_3()