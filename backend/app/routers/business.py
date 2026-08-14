from fastapi import APIRouter, Header, HTTPException

from ..catalog.merge import get_business
from ..config import ADMIN_TOKEN
from ..rag.ingest import reindex
from ..rag.retriever import _ensure_indexed

router = APIRouter(prefix="/api", tags=["business"])


def load(business_id: str) -> dict:
    try:
        return get_business(business_id)
    except ModuleNotFoundError:
        raise HTTPException(404, f"No such business: {business_id}")


@router.get("/business/{business_id}")
def business(business_id: str):
    b = load(business_id)
    return {k: b.get(k) for k in
            ("business_id", "business_name", "location", "avatar_url", "signature_items", "tagline")}


@router.get("/catalog/{business_id}")
def catalog(business_id: str):
    return load(business_id)["catalog"]


@router.post("/admin/reindex/{business_id}")
def admin_reindex(business_id: str, x_admin_token: str = Header("")):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(401, "Bad admin token")
    load(business_id)
    _ensure_indexed.cache_clear()
    return {"business_id": business_id, "chunks": reindex(business_id)}
