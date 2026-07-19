import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.engines.graph_rag import graph_rag_engine
from app.services.vector_store import vector_store_service
from app.services.graph_store import graph_store_service

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Ingestion Schema
class IngestPayload(BaseModel):
    url: str
    title: str
    cleaned_text: str
    metrics: Optional[Dict[str, Any]] = None

# Query Schema
class QueryPayload(BaseModel):
    query: str
    rag_mode: Optional[str] = "graphrag"

@app.get("/")
def read_root():
    return {"message": "Welcome to the Internet Memory Layer API"}

@app.post("/api/v1/capture/ingest", status_code=status.HTTP_202_ACCEPTED)
def ingest_page(payload: IngestPayload):
    """
    Ingests and indexes parsed page content, creating embeddings and database entries.
    """
    if not payload.url or not payload.cleaned_text:
        raise HTTPException(
            status_code=400, 
            detail="URL and Cleaned Text fields are required."
        )
        
    try:
        # 1. Simple chunking strategy (split by sentences/newlines)
        text_content = payload.cleaned_text
        chunks = [text_content[i:i+500] for i in range(0, len(text_content), 400)]
        
        # 2. Add to ChromaDB Vector Store
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{payload.url}_chunk_{idx}"
            # Generate a basic dummy embedding vectors (fallback if offline)
            emb = graph_rag_engine.generate_embedding(chunk)
            
            vector_store_service.add_document_chunks(
                ids=[chunk_id],
                embeddings=[emb],
                documents=[chunk],
                metadatas=[{
                    "url": payload.url,
                    "title": payload.title,
                    "chunk_index": idx
                }]
            )
            
        # 3. Simple Graph Ingestion: Register the URL/Title as a Concept node in Neo4j
        graph_store_service.create_concept_node(
            name=payload.title,
            category="Website",
            description=f"Webpage at {payload.url}"
        )
        
        return {
            "status": "queued",
            "message": "Ingestion task accepted successfully.",
            "chunks_created": len(chunks)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ingestion pipeline error: {str(e)}"
        )

@app.post("/api/v1/memory/ask")
def ask_memory(payload: QueryPayload):
    """
    Performs hybrid retrieval (Vector + Graph) to answer queries.
    """
    if not payload.query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    try:
        response = graph_rag_engine.ask_memory(payload.query)
        return response
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"GraphRAG inference failed: {str(e)}"
        )

@app.get("/api/v1/graph/nodes")
def get_graph_nodes(center_node: str, depth: int = 1):
    """
    Returns graph neighborhood relations for visualization.
    """
    try:
        subgraph = graph_store_service.query_subgraph(center_node=center_node, max_depth=depth)
        return subgraph
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch graph data: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
