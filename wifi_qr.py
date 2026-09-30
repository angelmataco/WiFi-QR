"""Genera un QR de conexión WiFi minimalista, listo para imprimir en un cuadro."""

import os
import sys
from pathlib import Path

import numpy as np
import qrcode
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont
from qrcode.constants import ERROR_CORRECT_H

# --- Configuración ---
OUTPUT_PATH = Path(__file__).parent / "wifi_qr.png"
TARGET_CM = 10
DPI = 300
TARGET_PX = int(TARGET_CM / 2.54 * DPI)  # ~1181 px

INITIAL_LOGO_RATIO = 0.22  # % del ancho del QR ocupado por el recuadro central
MIN_LOGO_RATIO = 0.10
RATIO_STEP = 0.02

SHOW_LABEL = True
LABEL_TEXT = "Wi-Fi"

FONT_CANDIDATES = [
    "/System/Library/Fonts/SFNS.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]


def escape_wifi_value(value: str) -> str:
    """Escapa \\, ;, ,, : y " según el estándar WIFI:// de QR."""
    for char in ("\\", ";", ",", ":", '"'):
        value = value.replace(char, "\\" + char)
    return value


def build_wifi_payload(ssid: str, password: str) -> str:
    return f"WIFI:T:WPA;S:{escape_wifi_value(ssid)};P:{escape_wifi_value(password)};;"


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


BADGE_ASSET_PATH = Path(__file__).parent / "assets" / "wifi_badge.png"


def render_badge(diameter: int) -> Image.Image:
    """Carga el badge (círculo + ícono de WiFi) ya recortado como imagen y lo
    escala al tamaño necesario. Es una imagen RGBA con fondo transparente
    fuera del círculo, lista para pegarse sobre el fondo blanco del QR.
    """
    badge = Image.open(BADGE_ASSET_PATH).convert("RGBA")
    return badge.resize((diameter, diameter), Image.LANCZOS)


def generate_qr_image(payload: str, logo_ratio: float) -> Image.Image:
    qr = qrcode.QRCode(
        error_correction=ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(payload)
    qr.make(fit=True)

    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    qr_width, qr_height = qr_img.size
    center = (qr_width / 2, qr_height / 2)

    halo_diameter = int(qr_width * logo_ratio)
    badge_img = render_badge(halo_diameter)

    paste_pos = (int(center[0] - halo_diameter / 2), int(center[1] - halo_diameter / 2))
    qr_img.paste(badge_img, paste_pos, badge_img)

    return qr_img


def add_label(qr_img: Image.Image, text: str) -> Image.Image:
    qr_width, qr_height = qr_img.size
    padding = qr_height // 12
    font_size = qr_width // 14
    font = load_font(font_size)

    tmp_draw = ImageDraw.Draw(qr_img)
    bbox = tmp_draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    final_img = Image.new(
        "RGB", (qr_width, qr_height + padding + text_h + padding), "white"
    )
    final_img.paste(qr_img, (0, 0))

    draw = ImageDraw.Draw(final_img)
    text_x = (qr_width - text_w) // 2
    text_y = qr_height + padding
    draw.text((text_x, text_y), text, fill="black", font=font)

    return final_img


def upscale_to_target(img: Image.Image, target_px: int) -> Image.Image:
    width, height = img.size
    scale = target_px / width
    new_size = (target_px, int(height * scale))
    return img.resize(new_size, Image.LANCZOS)


def verify_qr(img: Image.Image, expected_payload: str) -> bool:
    import cv2

    arr = np.array(img.convert("RGB"))
    arr_bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

    detector = cv2.QRCodeDetector()
    decoded_text, _, _ = detector.detectAndDecode(arr_bgr)

    return decoded_text == expected_payload


def main():
    load_dotenv()

    ssid = os.getenv("WIFI_SSID")
    password = os.getenv("WIFI_PASSWORD")

    if not ssid or not password:
        print(
            "Error: define WIFI_SSID y WIFI_PASSWORD en un archivo .env "
            "(usa .env.example como referencia)."
        )
        sys.exit(1)

    payload = build_wifi_payload(ssid, password)

    ratio = INITIAL_LOGO_RATIO
    final_img = None
    success = False

    while ratio >= MIN_LOGO_RATIO:
        qr_img = generate_qr_image(payload, ratio)

        if SHOW_LABEL:
            qr_img = add_label(qr_img, LABEL_TEXT)

        candidate = upscale_to_target(qr_img, TARGET_PX)

        if verify_qr(candidate, payload):
            final_img = candidate
            success = True
            break

        print(f"Verificación falló con logo_ratio={ratio:.2f}, reduciendo tamaño...")
        ratio -= RATIO_STEP

    if not success:
        print(
            "No se pudo generar un QR legible ni con el recuadro mínimo "
            f"({MIN_LOGO_RATIO:.2f}). Prueba reducir MIN_LOGO_RATIO o revisar el SSID/contraseña."
        )
        sys.exit(1)

    final_img.save(OUTPUT_PATH, dpi=(DPI, DPI))

    print(f"QR generado correctamente en: {OUTPUT_PATH}")
    print(f"Tamaño de recuadro central que funcionó: {ratio:.2f} ({ratio * 100:.0f}% del ancho del QR)")
    print(f"Resolución: {final_img.size[0]}x{final_img.size[1]} px @ {DPI} DPI")


if __name__ == "__main__":
    main()
