import re

# looks like an arithmetic expression or contains a percent with a number
MATH_HINT = re.compile(r'\d[\d\.\,\s]*([kmbtKMBT])?(\s*[+\-*/×÷]\s*\d|\s*\%)')

def decide_tasks(q: str) -> list[str]:
    ql = q.lower()

    # 1) math-first when we spot arithmetic or % patterns
    if MATH_HINT.search(q):
        return ["math", "graph", "vector"]

    # 2) graph-y questions
    if any(x in ql for x in ["ceo", "who is", "side effect", "interact", "revenue"]):
        return ["graph", "vector"]

    # 3) fallback: vector
    return ["vector"]

YEAR_RE = re.compile(r"\b(19|20)\d{2}\b")

# Simple dictionaries for intent hints
CEO_SYNS = ["ceo", "chief executive", "who runs", "head of"]
REV_SYNS = ["revenue", "sales", "turnover", "top line", "income"]
SIDE_SYNS = ["side effect", "adverse effect", "nausea", "diarrhea", "stomach upset"]
INTERACT_SYNS = ["interact", "interaction", "contraindication", "safe with"]
COMPANY_HINTS = ["tesla"]          # add more as needed
DRUG_HINTS    = ["metformin", "ibuprofen", "aspirin"]

def _contains_any(q: str, terms: list[str]) -> bool:
    ql = q.lower()
    return any(t in ql for t in terms)

def rewrite_question(q: str) -> str:
    """
    Light normalization to help downstream match the right Cypher.
    Examples:
      - "Tesla 2024"         -> "Tesla revenue 2024"
      - "who runs tesla"     -> "tesla ceo"
      - "metformin and aspirin" -> "does ibuprofen interact with aspirin?" (handled if you expand)
    """
    q2 = (q or "").strip()
    ql = q2.lower()

    # Company + Year -> assume they want revenue for that year
    if _contains_any(ql, COMPANY_HINTS) and YEAR_RE.search(ql) and not _contains_any(ql, REV_SYNS):
        q2 = q2 + " revenue"

    # CEO phrasing
    if any(s in ql for s in CEO_SYNS) and not _contains_any(ql, ["ceo"]):
        # normalize to "<company> ceo"
        for c in COMPANY_HINTS:
            if c in ql:
                q2 = f"{c} ceo"
                break

    # Side-effect phrasing
    if _contains_any(ql, DRUG_HINTS) and _contains_any(ql, ["side effects"]) is False:
        # if it mentions a known drug + a known side-effect synonym, hint with "side effects"
        if _contains_any(ql, SIDE_SYNS):
            for d in DRUG_HINTS:
                if d in ql:
                    q2 = f"{d} side effects"
                    break

    # Drug-drug interaction hint (very light)
    if "ibuprofen" in ql and "aspirin" in ql and not _contains_any(ql, INTERACT_SYNS):
        q2 = "does ibuprofen interact with aspirin?"

    return q2

from services.router.rl_policy import prefer_order  # if you added learning

def decide_tasks(question: str) -> list[str]:
    """
    Deterministic, simple routing:
    - If it looks numeric (% or K/M/B/T with digits): math → graph → vector
    - If it looks like a structured fact: graph → vector → math
    - Else: vector → graph → math
    """
    ql = (question or "").lower()

    # math-first: any digit + (% OR K/M/B/T suffix)
    if any(ch.isdigit() for ch in ql) and ("%" in ql or any(s in ql for s in ["k","m","b","t"])):
        return ["math", "graph", "vector"]

    # graphy hints (expand as you like)
    if any(x in ql for x in ["ceo", "who is", "side effect", "interact", "revenue", "earnings"]):
        return ["graph", "vector", "math"]

    # default: vector first
    return ["vector", "graph", "math"]
def combine_answers(graph_ans: str|None, vector_ans: str|None) -> str:
    """
    Prefer graph (facts). If vector adds new info not contained in graph,
    append it as additional context.
    """
    g = (graph_ans or "").strip()
    v = (vector_ans or "").strip()
    if g and v and v.lower() not in g.lower():
        return f"{g}\n\n(Additional context)\n{v}"
    return g or v or "No answer found."