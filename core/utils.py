import qrcode
from io import BytesIO
from django.http import HttpResponse
from PIL import Image, ImageDraw, ImageFont
from decouple import config

def generate_qr_image(qr_slug):
    # สร้าง URL เต็มสำหรับ Pet Card โดยใช้ SERVER_IP จาก .env
    base_url = config('SERVER_IP', default='http://localhost:8000')
    full_url = f"{base_url}/core/pet/{qr_slug}/card/"
    
    # สร้าง QR Code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(full_url)
    qr.make(fit=True)
    
    # สร้างรูปภาพ QR Code
    img = qr.make_image(fill_color="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# def generate_card_image(pet):
#     bg = Image.open("static/card_template.png").convert("RGBA")
#     draw = ImageDraw.Draw(bg)
#     font = ImageFont.truetype("static/fonts/Roboto-Regular.ttf", 22)
#     draw.text((150,40), pet.name, font=font, fill=(0,0,0))
#     qr = qrcode.make(f"https://yourdomain.com/pet/{pet.qr_slug}")
#     qr = qr.resize((180,180))
#     bg.paste(qr, (bg.width-220, 30))
#     buf = BytesIO()
#     bg.save(buf, format="PNG")
#     buf.seek(0)
#     return buf
