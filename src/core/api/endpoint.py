from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.core.api.business import chat

endpoint = APIRouter()


class ChatRequest(BaseModel):
    query_text: str
    field: str = None
    value: str = None
    limit: int = 10


@endpoint.get("/health")
def health():
    return {"message": "OK"}


@endpoint.post("/chat")
async def chat_endpoint(request: ChatRequest):
    stream = chat(
        query_text=request.query_text,
        field=request.field,
        value=request.value,
        limit=request.limit,
    )
    return StreamingResponse(stream, media_type="text/plain")
