from fastapi import APIRouter
from sqlmodel import Session, select

from ..models import Order, OrderCreate, engine

router = APIRouter(prefix="/api", tags=["orders"])


@router.post("/orders")
def create_order(payload: OrderCreate):
    order = Order(**payload.model_dump())
    with Session(engine) as db:
        db.add(order)
        db.commit()
        db.refresh(order)
    return {"order_id": order.id, "status": order.status}


@router.get("/orders/{business_id}")
def list_orders(business_id: str) -> list[Order]:
    with Session(engine) as db:
        return list(db.exec(
            select(Order).where(Order.business_id == business_id).order_by(Order.id.desc())))
