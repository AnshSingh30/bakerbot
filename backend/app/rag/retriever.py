from functools import lru_cache

from langchain_core.documents import Document

from .ingest import reindex, store


@lru_cache
def _ensure_indexed(business_id: str) -> None:
    """Index on first use so a fresh clone just works. Cached per process."""
    vs = store()
    if not vs.get(where={"business_id": business_id}, limit=1)["ids"]:
        reindex(business_id)


def retrieve(business_id: str, query: str, k: int = 5) -> list[Document]:
    _ensure_indexed(business_id)
    return store().similarity_search(query, k=k, filter={"business_id": business_id})
