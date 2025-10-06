# services/tools/math_eval.py
# Evaluates simple arithmetic with human-friendly numbers and percents.
# Examples:
#   "97B + 20%"  -> 116400000000.0
#   "97B - 20%"  -> 77600000000.0
#   "12M + 3.5B" -> 3512000000.0

import re
from services.tools.num_parse import parse_human_number

# Tokenize numbers (with optional K/M/B/T and optional %), operators, and parens
TOKEN_RE = re.compile(r"""
    \d+(?:\.\d+)?[KMBTkmbt]?%?   # 97B, 20%, 12.5M, 3.2K, 15
  | [+\-*/()]                    # + - * / ( )
""", re.X)

def _tokenize(s: str) -> list[str]:
    """Split an expression into tokens we can rewrite/parse."""
    return TOKEN_RE.findall(s.replace(' ', ''))

def _rewrite_percent(tokens: list[str]) -> list[str]:
    """
    Rewrite:
      A + B%  ->  ( A * ( 1 + B/100 ) )
      A - B%  ->  ( A * ( 1 - B/100 ) )
      A * B%  ->  ( A * ( B/100 ) )
      A / B%  ->  ( A / ( B/100 ) )
    Emits tokens (not a single string) so _to_python_expr can convert properly.
    """
    out = []
    i = 0

    def is_numlike(t: str) -> bool:
        return parse_human_number(t) is not None

    while i < len(tokens):
        t = tokens[i]
        # Pattern: base op pct%
        if (
            i >= 2
            and t.endswith('%')
            and tokens[i-1] in ['+', '-', '*', '/']
            and is_numlike(tokens[i-2])
        ):
            base_val = parse_human_number(tokens[i-2])
            op = tokens[i-1]
            pct = float(t[:-1]) / 100.0  # "20%" -> 0.2

            # remove the last two tokens we already appended (base and op)
            out = out[:-2]

            if op == '+':
                # ( base * ( 1 + pct ) )
                out.extend(['(', str(base_val), '*', '(', '1', '+', str(pct), ')', ')'])
            elif op == '-':
                # ( base * ( 1 - pct ) )
                out.extend(['(', str(base_val), '*', '(', '1', '-', str(pct), ')', ')'])
            elif op == '*':
                # ( base * ( pct ) )
                out.extend(['(', str(base_val), '*', str(pct), ')'])
            elif op == '/':
                # ( base / ( pct ) )
                if pct == 0:
                    # will be handled later as eval error; keep a safe non-zero to avoid ZeroDivision here
                    out.extend(['(', str(base_val), '/', '1e-18', ')'])
                else:
                    out.extend(['(', str(base_val), '/', str(pct), ')'])
            i += 1
            continue

        out.append(t)
        i += 1

    return out

def _to_python_expr(tokens: list[str]) -> str:
    """Convert tokens to a pure Python expression (numbers and operators)."""
    py = []
    for t in tokens:
        if t in ['+', '-', '*', '/', '(', ')']:
            py.append(t)
        else:
            # number-ish (may still carry K/M/B/T)
            val = parse_human_number(t) if not t.endswith('%') else None
            if val is None:
                # Leftover '%'-style tokens should have been rewritten; if any remains, try a last fallback
                if t.endswith('%'):
                    # "X%" -> (X/100)
                    x = t[:-1]
                    try:
                        x_val = float(x) / 100.0
                        py.append(str(x_val))
                        continue
                    except Exception:
                        raise ValueError(f"Unrecognized percent token: {t}")
                raise ValueError(f"Unrecognized token: {t}")
            py.append(str(val))
    return "".join(py)

def eval_math(expr: str):
    """Return a float result if we can evaluate, else None."""
    try:
        if not isinstance(expr, str):
            return None
        tokens = _tokenize(expr)
        tokens = _rewrite_percent(tokens)
        py = _to_python_expr(tokens)
        return eval(py, {"__builtins__": {}}, {})
    except Exception:
        return None