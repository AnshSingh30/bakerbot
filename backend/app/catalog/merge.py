"""baseline + overlay -> the one dict everything else reads."""
import importlib
from copy import deepcopy
from functools import lru_cache

from .baseline import BASELINE_CATALOG, BASELINE_FAQ


@lru_cache
def get_business(business_id: str) -> dict:
    """Merged business profile: overlay keys + `catalog` + `faq`.

    price_overrides / faq_overrides replace; extra_faq / signature_items append.
    Raises ModuleNotFoundError if there is no overlay for this id.
    """
    overlay = importlib.import_module(f".overlays.{business_id}", __package__).OVERLAY

    catalog = deepcopy(BASELINE_CATALOG)
    for category, items in overlay.get("price_overrides", {}).items():
        for item, price in items.items():
            current = catalog[category]["items"].get(item)
            if isinstance(current, dict) and isinstance(price, dict):
                current.update(price)
            else:
                catalog[category]["items"][item] = price

    faq = {**BASELINE_FAQ, **overlay.get("faq_overrides", {}), **overlay.get("extra_faq", {})}
    if overlay.get("always_eggless"):
        faq.pop("egg_option", None)

    return {
        **overlay,
        "tagline": f"{overlay.get('instagram_handle', '')} · {overlay.get('location', '')}".strip(" ·"),
        "catalog": catalog,
        "faq": faq,
    }


def prices(business_id: str) -> set[int]:
    """Every rupee figure that legitimately exists for this business."""
    out = set()
    for category in get_business(business_id)["catalog"].values():
        for price in category["items"].values():
            out.update(price.values() if isinstance(price, dict) else [price])
    return out


def list_businesses() -> list[str]:
    from pathlib import Path
    folder = Path(__file__).parent / "overlays"
    return sorted(p.stem for p in folder.glob("*.py") if not p.stem.startswith("_"))
