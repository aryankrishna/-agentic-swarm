from typing import Tuple
from time import perf_counter
from PIL import Image
import pytesseract
from io import BytesIO

def extract_text(image_bytes: bytes, *, lang: str = "eng") -> Tuple[str, int]:
    """Extract text from image bytes and return (text, latency_ms)."""
    t0 = perf_counter()
    try:
        img = Image.open(BytesIO(image_bytes)).convert("RGB")
    except Exception:
        return "", int((perf_counter() - t0) * 1000)
    text = pytesseract.image_to_string(img, lang=lang) or ""
    return text.strip(), int((perf_counter() - t0) * 1000)
