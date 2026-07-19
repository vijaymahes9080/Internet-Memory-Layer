import uvicorn
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from app.core.config import settings
from app.engines.graph_rag import graph_rag_engine
from app.services.vector_store import vector_store_service
from app.services.graph_store import graph_store_service
from app.engines.time_machine import time_machine_engine
from app.engines.curiosity import curiosity_engine
from app.engines.concept_dna import concept_dna_engine

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

# Time Machine Snapshot Schema
class SnapshotPayload(BaseModel):
    url: str
    title: str
    scroll_depth_percent: float
    trigger_event: str
    timestamp: str

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
            # Generate embedding vectors
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

# ----------------- CREATIVE INNOVATIONS API ROUTINGS -----------------

@app.post("/api/v1/timeline/snapshot", status_code=status.HTTP_201_CREATED)
def record_snapshot(payload: SnapshotPayload):
    """
    Logs active tab state snapshots into the local SQLite time machine index.
    """
    try:
        time_machine_engine.save_snapshot(
            url=payload.url,
            title=payload.title,
            scroll_depth=payload.scroll_depth_percent,
            trigger=payload.trigger_event,
            timestamp=payload.timestamp
        )
        return {"status": "recorded", "message": "State snapshot recorded successfully."}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record state snapshot: {str(e)}"
        )

@app.get("/api/v1/timeline/replay")
def replay_session(date: str):
    """
    Replays chronological browsing sequence snapshots matching a target date (YYYY-MM-DD).
    """
    try:
        snapshots = time_machine_engine.get_replay_session(date)
        return {"date": date, "snapshots": snapshots}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch replay sessions: {str(e)}"
        )

@app.get("/api/v1/curiosity/gaps")
def list_curiosity_gaps():
    """
    Finds concepts that are semantically close but unconnected, generating connection hypothesis.
    """
    try:
        gaps = curiosity_engine.detect_knowledge_gaps()
        return {"knowledge_gaps": gaps}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to detect gaps: {str(e)}"
        )

@app.get("/api/v1/curiosity/quiz")
def get_curiosity_quiz(topic: Optional[str] = None):
    """
    Generates study check questions for weak/new concept nodes in the graph.
    """
    try:
        quiz = curiosity_engine.generate_quiz(topic)
        return quiz
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compile quiz: {str(e)}"
        )

@app.get("/api/v1/concept/dna")
def get_concept_dna(concept: str):
    """
    Returns unique influence vectors, centrality scores, and fingerprint signatures.
    """
    try:
        dna = concept_dna_engine.get_concept_dna(concept)
        return dna
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compute concept DNA: {str(e)}"
        )

@app.get("/api/v1/concept/genome")
def get_knowledge_genome():
    """
    Returns high-level domain expertise metrics and temporal growth rates.
    """
    try:
        genome = concept_dna_engine.get_knowledge_genome()
        return genome
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate genome: {str(e)}"
        )

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
