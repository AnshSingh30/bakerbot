from fastapi import APIRouter

from ..models import ChatRequest, ChatResponse
from ..rag.chain import respond
from .business import load

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    load(req.business_id)          # 404 for an unknown business
    return respond(req.business_id, req.session_id, req.message)
