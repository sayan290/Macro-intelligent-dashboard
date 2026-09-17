from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json

from app.ai.ollama_client import OllamaClient
from app.ai.rag_pipeline import RAGPipeline
from app.database import get_redis

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    context: Optional[str] = None
    use_rag: bool = False
    stream: bool = False


class DocumentIngest(BaseModel):
    title: str
    content: str
    source: Optional[str] = None
    category: Optional[str] = "research"


@router.post("/chat")
async def chat(request: ChatRequest):
    """Send a message to the AI assistant."""
    ollama = OllamaClient()

    if request.use_rag:
        rag = RAGPipeline()
        context = await rag.query(request.message)
        augmented_message = f"""Based on the following research context, answer the question.

Context:
{context}

Question: {request.message}"""
    else:
        augmented_message = request.message

    if request.context:
        augmented_message = f"Additional context: {request.context}\n\n{augmented_message}"

    if request.stream:
        return StreamingResponse(
            ollama.stream_chat(augmented_message),
            media_type="text/event-stream",
        )

    response = await ollama.chat(augmented_message)
    return {"response": response, "source": "rag" if request.use_rag else "direct"}


@router.post("/analyze")
async def analyze_market(
    topic: str = "current macro environment",
):
    """Get AI analysis of the current macro environment."""
    redis = await get_redis()
    cache_key = f"ai:analysis:{topic}"
    cached = await redis.get(cache_key)
    if cached:
        return json.loads(cached)

    ollama = OllamaClient()
    prompt = f"""You are a senior macroeconomic analyst. Provide a concise, insightful analysis of: {topic}

Structure your analysis as:
1. Current State: What's happening now
2. Key Drivers: What factors are driving this
3. Risk Assessment: Key risks to monitor
4. Outlook: Near-term and medium-term outlook
5. Actionable Takeaways: What investors should consider

Be specific, data-driven, and avoid generic advice."""

    response = await ollama.chat(prompt)
    result = {"topic": topic, "analysis": response}

    await redis.setex(cache_key, 7200, json.dumps(result))
    return result


@router.post("/documents/ingest")
async def ingest_document(doc: DocumentIngest):
    """Ingest a research document into the RAG knowledge base."""
    rag = RAGPipeline()
    doc_id = await rag.ingest(
        title=doc.title,
        content=doc.content,
        source=doc.source,
        category=doc.category,
    )
    return {"document_id": doc_id, "message": "Document ingested successfully"}


@router.get("/documents")
async def list_documents():
    """List ingested documents."""
    rag = RAGPipeline()
    return await rag.list_documents()
