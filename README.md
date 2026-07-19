# Internet Memory Layer (IML)

**Internet Memory Layer (IML)** is a production-grade, local-first, privacy-first platform that turns your browsing history into an queryable knowledge system. Instead of search engines that only retrieve pages, IML connects ideas across websites, constructs an interactive knowledge graph, and lets you query your browsing history years later as if it were a digital second brain.

---

## 🚀 Key Architectural Features & Innovations

1. **Memory GraphRAG**: Answers generated directly from relationships between your personal entities (Concepts, Tech, companies, papers) in Neo4j and vector chunks in ChromaDB.
2. **Concept DNA & Knowledge Genome**: Computes centrality indices and vector fingerprints to track how your interests and expertise evolve over time.
3. **AI Curiosity Engine**: Automatically searches your graph for unconnected concepts that share highly similar text contents, highlighting "Knowledge Gaps" and designing flashcard quizzes.
4. **Internet Time Machine**: Chronologically logs scroll offsets and active visual durations, allowing you to slide-scrub and replay research sessions.
5. **Passive Ingestion Extension**: Background Chrome/Firefox Manifest V3 tracker running dwell-time visibility algorithms.

---

## 🛠 Tech Stack (100% Local / Open Source)

- **Frontend**: Next.js (React), TailwindCSS, Tauri Desktop (Rust Shell), D3.js / React Flow
- **Browser Extension**: Manifest V3 (Chrome, Firefox, Edge, Brave)
- **Backend**: FastAPI (Python), Uvicorn, SQLite & PostgreSQL
- **Vector DB**: ChromaDB & FAISS
- **Graph DB**: Neo4j (Bolt Connection)
- **Local AI**: Ollama (Qwen-2.5, DeepSeek-R1, BGE Embeddings)
- **Queue & Cache**: Redis

---

## 📂 Repository Structure

```
internet-memory-layer/
├── backend/                  # FastAPI Python backend
│   ├── app/
│   │   ├── core/             # Configuration managers
│   │   ├── engines/          # GraphRAG, Curiosity, Time Machine, Concept DNA
│   │   ├── services/         # Neo4j and ChromaDB drivers
│   │   └── main.py           # FastAPI server definitions
│   └── requirements.txt      # Python packages setup
├── extension/                # Browser extension (MV3)
│   ├── src/
│   │   └── background/       # Active tab state capturing service worker
│   └── manifest.json         # Extension registry config
├── docs/                     # Full architecture & API specs
│   ├── architecture.md
│   ├── pipelines.md
│   ├── API_developer.md
│   └── user_guide.md
├── LICENSE                   # MIT License
└── .gitignore                # Build and config exclusions
```

---

## ⚙ Local Setup (No Docker)

### 1. Local Database & AI Prereqs
1. Download and run **Ollama** locally. Pull the required models:
   ```bash
   ollama pull qwen2.5:1.5b
   ollama pull bge-large-en-v1.5
   ```
2. Download and run **Neo4j Desktop** or Community Edition locally, set the bolt endpoint password.
3. Make sure **Redis** is installed and active on `localhost:6379`.

### 2. Run Backend API
```bash
cd backend
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```
FastAPI docs will spin up on [http://localhost:8000/docs](http://localhost:8000/docs).

### 3. Install Browser Extension
1. Open Chrome and navigate to `chrome://extensions/`.
2. Enable **Developer Mode** (toggle on top right).
3. Click **Load unpacked** and select the `/extension` folder in this repository.

---

## 📄 License
Licensed under the [MIT License](LICENSE).
