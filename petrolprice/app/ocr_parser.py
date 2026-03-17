"""
Fetch fuel price board image from URL, run OCR, and parse Fuel section.
Returns list of {"fuel_type": str, "price": float}.
"""
import re
import logging
from io import BytesIO

import requests
import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)

# Regex to match a price at end of line (number with optional decimal, optional currency)
PRICE_RE = re.compile(r"(\d+[.,]\d{2})\s*$")


def fetch_image(image_url: str) -> Image.Image:
    """Download image from URL and return PIL Image."""
    resp = requests.get(image_url, timeout=30)
    resp.raise_for_status()
    img = Image.open(BytesIO(resp.content))
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    return img


def run_ocr(img: Image.Image) -> str:
    """Run Tesseract OCR and return full text (with layout)."""
    return pytesseract.image_to_string(img)


def parse_fuel_section(text: str) -> list[dict]:
    """
    Find "Fuel" category and parse lines below as fuel_type + price (price on right).
    Returns [{"fuel_type": str, "price": float}, ...].
    """
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    fuel_start = None
    for i, line in enumerate(lines):
        if line.lower() == "fuel":
            fuel_start = i + 1
            break
    if fuel_start is None:
        logger.warning("'Fuel' section not found in OCR text")
        return []

    result = []
    for line in lines[fuel_start:]:
        # Stop at empty or at next section (e.g. another category word)
        if not line:
            continue
        # Optional: stop at next known category headers
        if line.lower() in ("adblue", "shop", "services", "opening"):
            break

        match = PRICE_RE.search(line)
        if not match:
            continue
        price_str = match.group(1).replace(",", ".")
        try:
            price = float(price_str)
        except ValueError:
            continue
        fuel_type = line[: match.start()].strip()
        if not fuel_type:
            continue
        result.append({"fuel_type": fuel_type, "price": price})

    return result


def fetch_and_parse(image_url: str) -> list[dict]:
    """Fetch image from URL, run OCR, parse Fuel section. Returns list of {fuel_type, price}."""
    img = fetch_image(image_url)
    text = run_ocr(img)
    return parse_fuel_section(text)
