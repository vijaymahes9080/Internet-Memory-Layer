import requests
from app.core.config import settings
from app.services.vector_store import vector_store_service
from app.services.graph_store import graph_store_service
from typing import Dict, Any, List

class GraphRAGEngine:
    def __init__(self):
        self.ollama_url = f"{settings.OLLAMA_BASE_URL}/api/generate"

    def generate_embedding(self, text: str) -> List[float]:
        """
        Calls Ollama or local sentence-transformers to generate a vector embedding.
        In production, use local sentence-transformers library or Ollama API.
        """
        url = f"{settings.OLLAMA_BASE_URL}/api/embeddings"
        payload = {
            "model": settings.EMBEDDING_MODEL,
            "prompt": text
        }
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json().get("embedding", [0.0] * 1024)
        except Exception as e:
            # Fallback mock embedding if Ollama is not active locally during bootstrap
            print(f"Ollama embedding failure: {e}. Returning mock embedding.")
            return [0.1] * 1024

    def ask_memory(self, query: str) -> Dict[str, Any]:
        # Step 1: Generate Embedding for the search query
        query_embedding = self.generate_embedding(query)

        # Step 2: Retrieve Vector Store top-K chunks
        chunks = vector_store_service.query_similarity(query_embedding, top_k=3)
        context_texts = [c["text"] for c in chunks]

        # Step 3: Identify entity terms from query, retrieve Graph paths from Neo4j
        # We can extract potential entities from the query using simple checks or NLP.
        # Let's extract words that look like concepts.
        words = [w.strip("?,.!") for w in query.split() if w[0].isupper()]
        graph_contexts = []
        referenced_nodes = []

        for word in words:
            try:
                subgraph = graph_store_service.query_subgraph(center_node=word, max_depth=1)
                referenced_nodes.append(word)
                for edge in subgraph.get("edges", []):
                    graph_contexts.append(
                        f"({edge['source']}) -[:{edge['type']}]-> ({edge['target']})"
                    )
            except Exception as e:
                # Silently catch database failures if Neo4j is offline
                print(f"Neo4j subgraph fetch skipped for {word}: {e}")

        # Step 4: Construct Prompt with Vector + Graph context
        context_str = "\n".join([f"- Chunk: {txt}" for txt in context_texts])
        graph_str = "\n".join([f"- Relationship: {rel}" for rel in graph_contexts])

        system_prompt = (
            "You are the Internet Memory Layer AI. You answer user questions using "
            "their private browsing history fragments and knowledge graph associations. "
            "Cite sources where relevant."
        )

        user_prompt = f"""
Query: {query}

---
RETIREVED DATA CHUNKS:
{context_str if context_str else "No page content available."}

---
KNOWLEDGE GRAPH TUPLES:
{graph_str if graph_str else "No graph relations available."}
---

Answer:
"""

        payload = {
            "model": settings.OLLAMA_MODEL,
            "prompt": user_prompt,
            "system": system_prompt,
            "stream": False
        }

        # Step 5: Ask Ollama LLM to synthesize response
        try:
            res = requests.post(self.ollama_url, json=payload)
            res.raise_for_status()
            answer = res.json().get("response", "Could not synthesize response.")
        except Exception as e:
            answer = (
                f"Local LLM (Ollama) is offline or model '{settings.OLLAMA_MODEL}' is missing. "
                f"Unable to process text generation. Error details: {e}"
            )

        return {
            "answer": answer,
            "chunks_retrieved": [c["metadata"].get("url", "unknown") for c in chunks],
            "graph_nodes_referenced": referenced_nodes
        }

graph_rag_engine = GraphRAGEngine()
