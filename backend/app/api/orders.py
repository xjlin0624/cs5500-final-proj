from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from .deps import get_current_user, get_db
from ..models.order import Order
from ..models.order_item import OrderItem
from ..models.user import User
from ..schemas.order import OrderCreate, OrderRead
from ..schemas.order_item import OrderItemCreate, OrderItemRead

router = APIRouter(prefix="/orders", tags=["orders"])

DB = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


# ---------------------------------------------------------------------------
# Request / response schemas (defined inline — simple enough for a class project)
# ---------------------------------------------------------------------------

from pydantic import BaseModel


class OrderIngest(OrderCreate):
    """OrderCreate extended with an optional list of line items."""
    items: list[OrderItemCreate] = []


class OrderReadWithItems(OrderRead):
    items: list[OrderItemRead] = []

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("", response_model=OrderReadWithItems, status_code=status.HTTP_201_CREATED)
def ingest_order(body: OrderIngest, db: DB, current_user: CurrentUser) -> Order:
    """
    Create or update an order for the authenticated user.

    Upsert key: (user_id, retailer, retailer_order_id).
    When an order already exists the scalar fields are updated and all line
    items are replaced with the ones in the request body.
    """
    order = (
        db.query(Order)
        .filter(
            Order.user_id == current_user.id,
            Order.retailer == body.retailer,
            Order.retailer_order_id == body.retailer_order_id,
        )
        .first()
    )

    if order is None:
        order = Order(user_id=current_user.id)
        db.add(order)

    # Apply scalar fields from the request body
    for field, value in body.model_dump(exclude={"items"}).items():
        setattr(order, field, value)

    db.flush()  # assign order.id before inserting items

    # Replace items: delete old ones, insert new ones
    db.query(OrderItem).filter(OrderItem.order_id == order.id).delete()
    for item_data in body.items:
        db.add(OrderItem(
            order_id=order.id,
            user_id=current_user.id,
            **item_data.model_dump(),
        ))

    db.commit()
    db.refresh(order)
    return order
