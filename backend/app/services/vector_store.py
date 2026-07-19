import chromadb
from chromadb.config import Settings as ChromaSettings
from app.core.config import settings
from typing import List, Dict, Any

class VectorStoreService:
    def __init__(self):
        # Initialise ChromaDB Client
        self.client = chromadb.PersistentClient(
            path=settings.CHROMADB_PATH,
            settings=ChromaSettings(allow_reset=True)
        )
        self.collection = self.client.get_or_create_collection(
            name="page_chunks"
        )

    def add_document_chunks(
        self, 
        ids: List[str], 
        embeddings: List[List[float]], 
        documents: List[str], 
        metadatas: List[Dict[str, Any]]
    ):
        """
        Inserts page text chunks with embeddings and metadata fields.
        """
        self.collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )

    def query_similarity(
        self, 
        query_embedding: List[float], 
        top_k: int = 5, 
        filter_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieves matching chunks based on cosine similarity scores.
        """
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=filter_metadata
        )
        
        formatted_results = []
        if results and 'documents' in results and results['documents']:
            docs = results['documents'][0]
            ids = results['ids'][0]
            metas = results['metadatas'][0]
            distances = results['distances'][0] if 'distances' in results else [0.0]*len(docs)
            
            for idx in range(len(docs)):
                formatted_results.append({
                    "id": ids[idx],
                    "text": docs[idx],
                    "metadata": metas[idx],
                    "distance": distances[idx]
                })
        return formatted_results

vector_store_service = VectorStoreService()
