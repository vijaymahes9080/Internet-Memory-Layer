# Internet Memory Layer (IML): Developer Guide & Local Setup

This document specifies the REST/GraphQL APIs, CLI, SDK formats, Local Ingest, Security, Privacy models, and Installation guides.

---

## 1. REST & GraphQL API Specifications

### 1.1 Ingestion Endpoint
- **URL**: `/api/v1/capture/ingest`
- **Method**: `POST`
- **Headers**: `Content-Type: application/json`, `Authorization: Bearer <token>`
- **Request Body**:
  ```json
  {
    "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "title": "Artificial intelligence - Wikipedia",
    "html_content": "<body>...</body>",
    "cleaned_text": "Artificial intelligence (AI) is intelligence...",
    "metrics": {
      "scroll_depth_percent": 100.0,
      "dwell_time_seconds": 320
    }
  }
  ```
- **Response** (`202 Accepted`):
  ```json
  {
    "status": "queued",
    "job_id": "job_e71b2d9a-4cbf-4e20-990a-a7ee5df921a8"
  }
  ```

### 1.2 Memory AI Query Endpoint
- **URL**: `/api/v1/memory/ask`
- **Method**: `POST`
- **Request Body**:
  ```json
  {
    "query": "What framework is alternative to LlamaIndex?",
    "stream": false,
    "rag_mode": "graphrag"
  }
  ```
- **Response** (`200 OK`):
  ```json
  {
    "answer": "LangChain and Haystack are primary alternatives to LlamaIndex...",
    "sources": [
      {
        "url": "https://github.com/langchain",
        "title": "LangChain GitHub"
      }
    ],
    "graph_nodes_referenced": ["LlamaIndex", "LangChain", "Haystack"]
  }
  ```

### 1.3 Graph Navigation API
- **URL**: `/api/v1/graph/nodes`
- **Method**: `GET`
- **Query Params**: `center_node=LlamaIndex`, `depth=2`
- **Response** (`200 OK`):
  ```json
  {
    "nodes": [
      {"id": "LlamaIndex", "label": "Concept", "importance": 0.9},
      {"id": "LangChain", "label": "Concept", "importance": 0.8}
    ],
    "edges": [
      {"source": "LlamaIndex", "target": "LangChain", "type": "alternative_to"}
    ]
  }
  ```

---

## 2. Plugin & SDK Architecture

IML supports custom plugins to ingest data from third-party platforms (GitHub, YouTube, Slack).

### 2.1 Python SDK Example
```python
from iml import IMLClient

client = IMLClient(base_url="http://localhost:8000", api_key="iml_dev_key")

# Ingest an item
client.ingest(
    url="https://github.com/trending",
    title="GitHub Trending",
    cleaned_text="Trending repositories today...",
    metrics={"dwell_time_seconds": 30}
)

# Search
results = client.search("GraphRAG alternatives")
print(results.answer)
```

### 2.2 Extension Plugin SDK (JS/TS)
Plugins run in safe sandboxes and export a single registration function:
```typescript
import { IMLPlugin } from '@iml/extension-sdk';

export default const myPlugin: IMLPlugin = {
  name: "GitHub Ingest",
  matchUrl: "*://github.com/*",
  onPageLoad: async (document) => {
    const stars = document.querySelector('.js-social-count')?.textContent;
    return {
      metadata: { github_stars: parseInt(stars || "0") }
    };
  }
};
```

---

## 3. Local Installation Guide (No Docker)

Set up IML locally on your system using Python, Node, and standalone database installations.

### 3.1 Prerequisites
1. **Python 3.11+**: For the FastAPI backend.
2. **Node.js 18+**: For the Next.js frontend and browser extension compile.
3. **Neo4j Desktop or Community Edition**: Installed locally.
4. **PostgreSQL / SQLite**: SQLite is default for zero-config; PostgreSQL can be configured.
5. **Redis**: Windows local MSI setup or running as native local service.
6. **Ollama**: Installed and running locally.

### 3.2 Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Configure settings (.env)
cp .env.example .env

# Run development server
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

### 3.3 Frontend & Tauri Desktop Setup
```bash
# Navigate to frontend directory
cd frontend

# Install packages
npm install

# Run frontend server locally
npm run dev

# Or build and launch native Tauri Desktop shell
npm run tauri dev
```

### 3.4 Ollama Setup
```bash
# Pull required models locally
ollama pull deepseek-r1:1.5b
ollama pull qwen2.5:1.5b
ollama pull bge-large-en-v1.5
```

---

## 4. Security & Privacy Architecture

IML enforces strict privacy-first, local-only defaults:
- **Local Keycloak**: Can be run locally to manage OAuth logins and user profiles securely.
- **Zero Remote Storage**: Data is saved to your local SQLite/PostgreSQL, local Neo4j, and local ChromaDB filesystems. No analytics are sent to external services.
- **Encryption at Rest**: Databases are encrypted using SQLCipher (for SQLite) and custom encrypted columns using Fernet encryption in SQL schemas.
- **Offline Mode**: If internet access is severed, vector matches and local LLMs continue to operate fully.

---

## 5. Performance Optimizations

To handle thousands of web pages smoothly:
- **ChromaDB Indexing**: Configured with `HNSW` (Hierarchical Navigable Small World) index for fast approximate nearest neighbor lookups.
- **Redis Cache**: Caches top query requests, entity embeddings, and active scraper page buffers.
- **Neo4j Connection Pool**: Configured with driver connection pooling to handle frequent write locks during mass batch document extractions.
- **Celery Task Limits**: Restricts concurrency of NLP extractions based on available system CPU/GPU cores to prevent desktop lags.
