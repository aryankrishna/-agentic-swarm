# --- stdlib & setup ---
import sys, re, datetime, json
from time import perf_counter
from pathlib import Path
import streamlit as st

# router / bandit
from services.router.bandit import (
    EpsGreedyBandit,
    offline_learn_from_csv,
    reward_from_row,
)

# Absolute, stable paths
ROOT = Path(__file__).resolve().parents[2]   # -> /app inside the container
DATA_DIR = ROOT / "data"
LOGS_DIR = DATA_DIR / "logs"
LOGS_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOGS_DIR / "app_events.log"

# Make project root importable
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def log_event(question, mode):
    event = {
        "timestamp": datetime.datetime.now().isoformat(),
        "question": question,
        "mode": mode,
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")

# --- third-party & app modules ---
from dotenv import load_dotenv
load_dotenv()

# tools & pipelines
from services.vector.query_tfidf import query_vector
from services.graph.graph_qa import query_graph
from services.router.logger import log_route
from services.agent.planner import decide_tasks, rewrite_question, combine_answers
from services.tools.math_eval import eval_math
from services.tools.num_parse import parse_human_number  # (used by math_eval)
from services.tools.ocr import extract_text

# ---------------- UI ----------------
st.set_page_config(page_title="Agentic Swarm — Vector + Graph RAG", page_icon="🧭")
st.title("Agentic Swarm — RAG Demo (Vector + Graph + Router)")

# warm/start the bandit from existing logs (cheap + fast)
bandit = offline_learn_from_csv()

mode = st.sidebar.radio("Mode", ["Vector (TF-IDF)", "Graph (Neo4j)", "Auto (Router)"])
k = st.sidebar.slider("Top-k (Vector)", 1, 8, 4, 1)
q = st.text_input("Ask a question (e.g., 'Metformin side effects', 'Who is Tesla’s CEO?')")

# Optional image -> OCR (done once; we reuse the text later)
img_file = st.file_uploader("Optional: attach an image with text (PNG/JPG)", type=["png","jpg","jpeg"])
ocr_text, ocr_latency = "", None
if img_file is not None:
    try:
        img_bytes = img_file.getvalue()
        ocr_text, ocr_latency = extract_text(img_bytes, lang="eng")
        with st.expander("📄 OCR text (from image)"):
            st.write(ocr_text if ocr_text else "(no text detected)")
    except Exception as e:
        st.warning(f"OCR failed: {e}")

# ---------------- Main ----------------
if st.button("Ask"):
    # must have either typed text or OCR text
    if not q and not ocr_text:
        st.warning("Type a question or upload an image.")
        st.stop()

    # Merge typed text + OCR (if present)
    if q and ocr_text:
        base_query = f"{q}\n\n[Image OCR]: {ocr_text}"
    elif ocr_text:
        base_query = ocr_text
    else:
        base_query = q

    log_event(base_query, mode)
    t0 = perf_counter()
    q2 = rewrite_question(base_query)

    # --- FAST PATH: pure math gets answered immediately ---
    if eval_math(q2) is not None and re.fullmatch(r"[0-9\.\s\+\-\*/()%KMBT]+", q2):
        ans = eval_math(q2)
        decision_used = "math"
        latency_ms = int((perf_counter() - t0) * 1000)

        st.subheader("Final Answer ↪")
        st.write(ans)

        # Log + bandit update
        log_route(base_query, decision_used, 1, latency_ms, rewritten=q2)
        try:
            r = reward_from_row({"decision": decision_used, "had_answer": 1, "latency_ms": latency_ms})
            bandit.update(decision_used, r)
        except Exception:
            pass

        st.stop()
    # --- end fast path ---

    # Decide which tools to try (order matters)
    if mode == "Vector (TF-IDF)":
        tasks = ["vector"]
        router_caption = "VECTOR (manual)"
    elif mode == "Graph (Neo4j)":
        tasks = ["graph"]
        router_caption = "GRAPH (manual)"
    else:
        planner_tasks = decide_tasks(q2)  # e.g., ["math","graph","vector"]
        if len(planner_tasks) > 1:
            chosen = bandit.select()  # one of ["vector","graph","math"]
            if chosen == "math":
                tasks = ["math"] + [t for t in planner_tasks if t != "math"]
            elif chosen == "graph":
                tasks = ["graph"] + [t for t in planner_tasks if t != "graph"]
            else:
                tasks = ["vector"] + [t for t in planner_tasks if t != "vector"]
            router_caption = "AGENT (bandit + planner)"
        else:
            tasks = planner_tasks
            router_caption = "AGENT (planner)"

    st.caption(f"Router decision: {router_caption}")

    # Running state
    decision_used = None
    final_answer = None  # can be str OR number
    graph_ans = None
    vector_ans = None
    graph_sources = []

    # Try each task until we get a usable answer
    for tool in tasks:
        if tool == "math":
            ans = eval_math(q2)
            if ans is not None:
                decision_used = "math"
                final_answer = ans
                break

        elif tool == "graph":
            ans, sources = query_graph(q2)
            if ans and str(ans).strip():
                decision_used = "graph"
                graph_ans = ans
                graph_sources = sources or []
                final_answer = ans
                break

        elif tool == "vector":
            docs, metas, ids, v_latency = query_vector(q2, k=k)
            if docs and docs[0].strip():
                snippet = docs[0][:800] + ("..." if len(docs[0]) > 800 else "")
                decision_used = "vector"
                vector_ans = snippet
                final_answer = snippet
                break

    # If nothing answered yet but we have partials, try to combine (optional)
    if final_answer is None:
        final_answer = combine_answers(graph_ans, vector_ans)

    # Compute latency and “has_answer”
    latency_ms = int((perf_counter() - t0) * 1000)
    has_answer = bool(final_answer.strip()) if isinstance(final_answer, str) else (final_answer is not None)

    # ----------- Render -----------
    st.subheader("Final Answer ↪")
    st.write(final_answer if has_answer else "Sorry, I don’t know how to answer that yet (graph).")

    if graph_sources:
        st.subheader("Graph Sources")
        for s in graph_sources:
            st.write(f"- {s}")

    with st.expander("debug"):
        st.write(
            {
                "question": q,
                "rewritten": q2,
                "tasks": tasks,
                "decision_used": decision_used,
                "graph_ans?": bool(graph_ans),
                "vector_ans?": bool(vector_ans),
                "ocr_chars": len(ocr_text) if ocr_text else 0,
                "ocr_latency_ms": ocr_latency,
                "latency_ms": latency_ms,
            }
        )

    # ----------- Log + bandit update -----------
    decision_to_log = decision_used or ("graph" if tasks == ["graph"] else "vector")
    log_route(base_query, decision_to_log, int(has_answer), latency_ms, rewritten=q2)
    try:
        row = {"decision": decision_to_log, "had_answer": int(has_answer), "latency_ms": latency_ms}
        r = reward_from_row(row)
        bandit.update(decision_to_log, r)
    except Exception:
        pass

st.sidebar.markdown("----")
st.sidebar.caption("✅ App Status: Running")