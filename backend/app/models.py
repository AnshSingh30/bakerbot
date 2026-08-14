from datetime import datetime
from typing import Optional

from pydantic import BaseModel
from sqlmodel import Field, SQLModel, create_engine

from .config import DATABASE_URL


class OrderDraft(BaseModel):
    """What the bot has managed to pin down so far."""
    item: str
    category: Optional[str] = None
    size: Optional[str] = None
    flavour: Optional[str] = None
    quantity: int = 1
    delivery_date: Optional[str] = None   # ISO date
    area: Optional[str] = None
    price: Optional[int] = None
    notes: Optional[str] = None


class ChatRequest(BaseModel):
    business_id: str
    session_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    order_draft: Optional[OrderDraft] = None
    grounded: bool = True
    sources: list[str] = []


class OrderCreate(OrderDraft):
    business_id: str
    customer_name: str
    customer_phone: str


class Order(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    business_id: str = Field(index=True)
    customer_name: str
    customer_phone: str
    item: str
    category: Optional[str] = None
    size: Optional[str] = None
    flavour: Optional[str] = None
    quantity: int = 1
    delivery_date: Optional[str] = None
    area: Optional[str] = None
    price: Optional[int] = None
    notes: Optional[str] = None
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.utcnow)


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def init_db() -> None:
    SQLModel.metadata.create_all(engine)
