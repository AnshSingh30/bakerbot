"""Catalog -> one atomic chunk per item / per FAQ entry -> Chroma."""
from langchain_chroma import Chroma

from ..catalog.merge import get_business
from ..config import CHROMA_DIR, get_embeddings

COLLECTION = "bakerbot"


def chunks(business_id: str) -> list[tuple[str, str, dict]]:
    """(id, text, metadata) — ids are deterministic so reindexing is idempotent."""
    b = get_business(business_id)
    out: list[tuple[str, str, dict]] = []

    for category, block in b["catalog"].items():
        pretty = category.replace("_", " ")
        for item, price in block["items"].items():
            bits = [f"{item} — {pretty}, {block['unit']}."]
            if isinstance(price, dict):
                bits.append("Price: " + ", ".join(
                    f"{'starting at' if k == 'starting_at' else k} ₹{v}" for k, v in price.items()) + ".")
            else:
                bits.append(f"Price: ₹{price} ({block['unit']}).")
            bits.append(f"Needs {block['lead_time_days']} day(s) advance notice.")
            if block.get("min_order_qty"):
                bits.append(f"Minimum order: {block['min_order_qty']}.")
            if block.get("note"):
                bits.append(block["note"])
            out.append((
                f"{business_id}:item:{category}:{item}",
                " ".join(bits),
                {"business_id": business_id, "kind": "item", "category": category, "item": item},
            ))

    for key, answer in b["faq"].items():
        out.append((
            f"{business_id}:faq:{key}",
            f"FAQ — {key.replace('_', ' ')}: {answer}",
            {"business_id": business_id, "kind": "faq", "category": "", "item": key},
        ))

    if b.get("signature_items"):
        out.append((
            f"{business_id}:signature",
            f"{b['business_name']} is best known for: {', '.join(b['signature_items'])}. "
            f"Based in {b.get('location', '')}. These are custom/theme work — priced by quote.",
            {"business_id": business_id, "kind": "faq", "category": "", "item": "signature"},
        ))
    return out


def store() -> Chroma:
    return Chroma(collection_name=COLLECTION, persist_directory=CHROMA_DIR,
                  embedding_function=get_embeddings())


def reindex(business_id: str) -> int:
    rows = chunks(business_id)
    ids = [r[0] for r in rows]
    vs = store()
    vs.delete(ids=ids)
    vs.add_texts([r[1] for r in rows], metadatas=[r[2] for r in rows], ids=ids)
    return len(rows)
