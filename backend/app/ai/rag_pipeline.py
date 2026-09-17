import chromadb
from typing import Optional
import hashlib
import structlog

from app.config import get_settings

logger = structlog.get_logger()


class RAGPipeline:
    """Retrieval-Augmented Generation pipeline using ChromaDB."""

    COLLECTION_NAME = "macro_research"

    def __init__(self):
        settings = get_settings()
        try:
            self.client = chromadb.HttpClient(host=settings.chroma_url.replace("http://", "").split(":")[0],
                                               port=int(settings.chroma_url.split(":")[-1]))
            self.collection = self.client.get_or_create_collection(
                name=self.COLLECTION_NAME,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as e:
            logger.warning("ChromaDB not available", error=str(e))
            self.client = None
            self.collection = None

    async def ingest(
        self,
        title: str,
        content: str,
        source: str = None,
        category: str = "research",
    ) -> str:
        """Ingest a document into the vector store."""
        if not self.collection:
            return "chromadb_unavailable"

        doc_id = hashlib.md5(f"{title}:{content[:100]}".encode()).hexdigest()

        # Chunk content for better retrieval
        chunks = self._chunk_text(content, chunk_size=500, overlap=50)

        ids = [f"{doc_id}_{i}" for i in range(len(chunks))]
        metadatas = [
            {"title": title, "source": source or "", "category": category, "chunk": i}
            for i in range(len(chunks))
        ]

        try:
            self.collection.add(
                documents=chunks,
                ids=ids,
                metadatas=metadatas,
            )
            logger.info("Document ingested", title=title, chunks=len(chunks))
            return doc_id
        except Exception as e:
            logger.error("Ingestion error", error=str(e))
            return f"error:{str(e)}"

    async def query(self, question: str, n_results: int = 5) -> str:
        """Query the vector store for relevant context."""
        if not self.collection:
            return "No research documents available. ChromaDB is not connected."

        try:
            results = self.collection.query(
                query_texts=[question],
                n_results=n_results,
            )
            if results and results["documents"]:
                docs = results["documents"][0]
                metas = results["metadatas"][0] if results["metadatas"] else [{}] * len(docs)
                context_parts = []
                for doc, meta in zip(docs, metas):
                    source = meta.get("title", "Unknown")
                    context_parts.append(f"[{source}]: {doc}")
                return "\n\n".join(context_parts)
            return "No relevant documents found."
        except Exception as e:
            logger.error("RAG query error", error=str(e))
            return f"Error querying knowledge base: {str(e)}"

    async def list_documents(self) -> list[dict]:
        """List all ingested documents."""
        if not self.collection:
            return []

        try:
            result = self.collection.get(limit=100)
            docs = {}
            for meta in result.get("metadatas", []):
                title = meta.get("title", "Unknown")
                if title not in docs:
                    docs[title] = {
                        "title": title,
                        "source": meta.get("source", ""),
                        "category": meta.get("category", ""),
                        "chunks": 0,
                    }
                docs[title]["chunks"] += 1
            return list(docs.values())
        except Exception as e:
            logger.error("List docs error", error=str(e))
            return []

    def _chunk_text(self, text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
        """Split text into overlapping chunks."""
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i:i + chunk_size])
            chunks.append(chunk)
            i += chunk_size - overlap
        return chunks if chunks else [text]
