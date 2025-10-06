# Agentic Swarm — Starter Skeleton
An advanced Retrieval-Augmented Generation (RAG) system that combines Vector Search (TF-IDF), Graph Database (Neo4j), Optical Character Recognition (OCR), and an adaptive Bandit Router to intelligently decide which knowledge source or reasoning path to use.


          ┌────────────┐
          │  User UI   │  ← Streamlit Frontend
          └────┬───────┘
               │
               ▼
     ┌────────────────────┐
     │  Agentic Router    │──→ decides best path
     └────────────────────┘
         │        │         │
         ▼        ▼         ▼
   (TF-IDF)   (GraphDB)   (Math/OCR)
   Vector →   Neo4j →      Tools →
   Returns     Paths        Context

   🧰 Tech Stack
	•	Python 3.11
	•	Streamlit (frontend)
	•	Neo4j 5 (Graph DB)
	•	scikit-learn / TfidfVectorizer
	•	pytesseract + Pillow (OCR)
	•	Docker Compose (multi-service orchestration)

# 1️⃣ Clone the repo
git clone https://github.com/aryankrishna/-agentic-swarm.git
cd agentic-swarm

# 2️⃣ Build and launch the containers
docker compose -f infra/docker-compose.yml up --build

# 3️⃣ Visit the app
# Streamlit UI → http://localhost:8501
# Neo4j Browser → http://localhost:7474 (user: neo4j, pass: testtest)

Text:

Who is the CEO of Tesla?
✅ Answer: Elon Musk

Math:

100 − 20
✅ Answer: 80.0

Image (OCR):

Upload an image that says “Who is the CEO of Tesla?”
✅ Answer: Elon Musk


agentic-swarm/
│
├── apps/ui/app.py                  # Streamlit front-end
├── services/
│   ├── graph/graph_qa.py           # Neo4j query logic
│   ├── vector/query_tfidf.py       # Vector search
│   ├── tools/ocr.py                # OCR extraction
│   ├── tools/math_eval.py          # Math tool
│   └── agent/planner.py            # Router planner logic
│
├── infra/docker-compose.yml        # App + Neo4j services
├── Dockerfile                      # Builds app container
├── data/                           # Logs, vector store, docs
└── requirements.txt                # Python dependencies


NEO4J_URI
Neo4j Bolt URI
bolt://graph:7687

NEO4J_USER
Username
neo4j

NEO4J_PASSWORD
Password
testtest

🧠 Future Enhancements
	•	Integrate LLM-based reasoning for hybrid RAG
	•	Add LangChain / FAISS / OpenAI Embeddings
	•	Deploy via AWS ECS / GCP Cloud Run
	•	Introduce feedback-based bandit retraining



This is the Phase 0 starter repo.
