"""Vector store service for RAG (Retrieval-Augmented Generation)."""

import os
from typing import List, Dict, Any, Optional
import numpy as np


class VectorStore:
    """Base vector store interface."""
    
    def __init__(self):
        self.initialized = False
    
    def initialize(self):
        """Initialize the vector store."""
        pass
    
    def add_documents(self, documents: List[str], embeddings: List[List[float]], metadata: List[Dict[str, Any]] = None):
        """Add documents to the vector store."""
        pass
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        pass


class FAISSVectorStore(VectorStore):
    """FAISS-based local vector store."""
    
    def __init__(self, index_path: str = "./data/faiss_index"):
        super().__init__()
        self.index_path = index_path
        self.index = None
        self.documents = []
        self.metadata = []
    
    def initialize(self):
        """Initialize FAISS index."""
        try:
            import faiss
            # For now, create a simple in-memory index
            # In production, this would load/save from disk
            self.index = None  # Will be created on first add
            self.initialized = True
        except ImportError:
            raise ImportError("faiss-cpu is required for FAISS vector store")
    
    def add_documents(self, documents: List[str], embeddings: List[List[float]], metadata: List[Dict[str, Any]] = None):
        """Add documents to FAISS index."""
        if not self.initialized:
            self.initialize()
        
        import faiss
        
        embeddings_array = np.array(embeddings, dtype=np.float32)
        dimension = embeddings_array.shape[1]
        
        if self.index is None:
            self.index = faiss.IndexFlatL2(dimension)
        
        self.index.add(embeddings_array)
        self.documents.extend(documents)
        if metadata:
            self.metadata.extend(metadata)
        else:
            self.metadata.extend([{}] * len(documents))
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        if not self.initialized or self.index is None:
            return []
        
        query_array = np.array([query_embedding], dtype=np.float32)
        distances, indices = self.index.search(query_array, top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < len(self.documents):
                results.append({
                    "document": self.documents[idx],
                    "metadata": self.metadata[idx],
                    "distance": float(distances[0][i]),
                })
        
        return results


class PineconeVectorStore(VectorStore):
    """Pinecone-based vector store."""
    
    def __init__(self, api_key: str, environment: str, index_name: str):
        super().__init__()
        self.api_key = api_key
        self.environment = environment
        self.index_name = index_name
        self.index = None
    
    def initialize(self):
        """Initialize Pinecone connection."""
        try:
            # Try new Pinecone client (v3+)
            try:
                from pinecone import Pinecone, ServerlessSpec
                pc = Pinecone(api_key=self.api_key)
                self.index = pc.Index(self.index_name)
                self.initialized = True
                return
            except ImportError:
                pass
            
            # Fallback to old Pinecone client (v2)
            try:
                import pinecone
                pinecone.init(api_key=self.api_key, environment=self.environment)
                self.index = pinecone.Index(self.index_name)
                self.initialized = True
            except ImportError:
                raise ImportError("pinecone-client is required for Pinecone vector store")
        except Exception as e:
            raise Exception(f"Failed to initialize Pinecone: {str(e)}")
    
    def add_documents(self, documents: List[str], embeddings: List[List[float]], metadata: List[Dict[str, Any]] = None):
        """Add documents to Pinecone index."""
        if not self.initialized:
            self.initialize()
        
        # Prepare vectors for Pinecone
        vectors = []
        for i, (doc, embedding) in enumerate(zip(documents, embeddings)):
            vector_id = f"doc_{i}"
            meta = metadata[i] if metadata and i < len(metadata) else {}
            meta["text"] = doc
            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": meta
            })
        
        # Upsert to Pinecone (batch processing recommended for production)
        # Handle both v2 and v3 API
        if hasattr(self.index, 'upsert'):
            if isinstance(vectors[0], dict):
                # v3 API
                self.index.upsert(vectors=vectors)
            else:
                # v2 API
                self.index.upsert(vectors=[(v["id"], v["values"], v["metadata"]) for v in vectors])
    
    def search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        if not self.initialized:
            return []
        
        try:
            # Try v3 API first
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )
            
            # Handle both response formats
            if hasattr(results, 'matches'):
                matches = results.matches
            elif isinstance(results, dict) and 'matches' in results:
                matches = results['matches']
            else:
                matches = []
            
            return [
                {
                    "document": match.get("metadata", {}).get("text", "") if isinstance(match, dict) else match.metadata.get("text", ""),
                    "metadata": {k: v for k, v in (match.get("metadata", {}) if isinstance(match, dict) else match.metadata).items() if k != "text"},
                    "score": match.get("score", 0.0) if isinstance(match, dict) else match.score,
                }
                for match in matches
            ]
        except Exception as e:
            # Return empty on error
            return []


def get_vector_store() -> Optional[VectorStore]:
    """
    Get vector store instance based on configuration.
    
    Returns:
        VectorStore instance or None if not configured
    """
    from app.config import settings
    
    if settings.use_faiss:
        store = FAISSVectorStore(index_path=settings.faiss_index_path)
        try:
            store.initialize()
            return store
        except Exception:
            return None
    
    if settings.pinecone_api_key:
        store = PineconeVectorStore(
            api_key=settings.pinecone_api_key,
            environment=settings.pinecone_environment or "",
            index_name=settings.pinecone_index_name or "script-foundary"
        )
        try:
            store.initialize()
            return store
        except Exception:
            return None
    
    return None

