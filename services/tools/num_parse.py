# services/tools/num_parse.py
import re

_UNIT = {
    'K': 1e3, 'k': 1e3,
    'M': 1e6, 'm': 1e6,
    'B': 1e9, 'b': 1e9,
    'T': 1e12,'t': 1e12,
}

def parse_human_number(text: str):
    """
    Extract the first number in text like $97B, 12.3M, 5k, 1,234,567
    Returns float or None.
    """
    if not isinstance(text, str):
        return None

def format_human_number(n: float) -> str:
    """
    Turn raw numbers into human-friendly strings.
    Example: 97000000000.0 -> 97.0B
    """
    absn = abs(n)
    for unit, div in [("T", 1e12), ("B", 1e9), ("M", 1e6), ("K", 1e3)]:
        if absn >= div:
            return f"{n/div:.1f}{unit}"
    return f"{n:.2f}"

    m = re.search(r'([$]?\s*\d[\d,\.]*\s*[bmkBMK]?)', text)
    if not m:
        return None
    chunk = m.group(1).replace(',', '').strip().lstrip('$')

    mult = 1.0
    if chunk.lower().endswith('b'):
        mult = 1e9
        chunk = chunk[:-1]
    elif chunk.lower().endswith('m'):
        mult = 1e6
        chunk = chunk[:-1]
    elif chunk.lower().endswith('k'):
        mult = 1e3
        chunk = chunk[:-1]

    try:
        return float(chunk) * mult
    except Exception:
        return None


def parse_human_number(s: str):
    """
    Parses strings like '97B', '12.5M', '1,234', '2.3k'
    Returns float or None.
    """
    if not isinstance(s, str):
        return None
    txt = s.strip().replace(',', '')
    m = re.fullmatch(r'([-+]?\d*\.?\d+)\s*([kKmMbBtT])?', txt)
    if not m:
        return None
    val = float(m.group(1))
    unit = m.group(2)
    if unit:
        val *= _UNIT[unit]
    return val