"""Structured slot-filling. The LLM returns its reply AND the order slots in one
call, so there is no second round-trip per turn."""
import re
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from ..models import OrderDraft


class BotTurn(BaseModel):
    """The WhatsApp reply plus every order detail known so far."""

    reply: str = Field(description="The WhatsApp message to send. 2-4 short lines, "
                                   "same language as the customer.")
    grounded: bool = Field(default=True, description="False if you had to decline or hedge "
                                                     "because the catalog/FAQ context did not cover the question.")
    item: Optional[str] = Field(default=None, description="The catalog item name exactly as it appears "
                                                          "in the context, e.g. 'Chocolate Truffle' or "
                                                          "'Fudge Brownie'. Never a category like 'cakes'.")
    size: Optional[str] = Field(default=None, description="e.g. '1kg', 'box of 6'.")
    flavour: Optional[str] = None
    quantity: int = Field(default=1)
    delivery_date: Optional[str] = Field(default=None, description="ISO yyyy-mm-dd, resolved date only.")
    area: Optional[str] = Field(default=None, description="Delivery area/locality.")
    price: Optional[int] = Field(default=None, description="Total in rupees, only if it appears in context.")
    notes: Optional[str] = Field(default=None, description="Custom message, theme, toppers.")
    ready: bool = Field(default=False, description="True only when item, size/qty, date and area are all "
                                                   "known AND the date passes the lead-time check.")

    @field_validator("price", mode="before")
    @classmethod
    def _digits_only(cls, value):
        """Models like to answer 'starting at ₹2,000' for an int field."""
        if isinstance(value, str):
            digits = re.sub(r"\D", "", value)
            return int(digits) if digits else None
        return value


SLOTS = ("item", "size", "flavour", "quantity", "delivery_date", "area", "price", "notes")


def merge_slots(previous: dict, turn: BotTurn) -> dict:
    """Sticky slots: a turn that stays silent about a slot doesn't erase it."""
    out = dict(previous)
    for slot in SLOTS:
        value = getattr(turn, slot)
        if value in (None, ""):
            continue
        if slot == "quantity" and value == 1:        # the default, not a real answer
            continue
        out[slot] = value
    return out


def to_draft(slots: dict, category: str | None) -> Optional[OrderDraft]:
    if not slots.get("item"):
        return None
    known = {k: v for k, v in slots.items() if k in SLOTS and v is not None}
    return OrderDraft(category=category, **known)
