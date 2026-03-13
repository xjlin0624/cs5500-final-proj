import uuid

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base
from .enums import MonitoringStoppedReason


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    product_name = Column(String(500), nullable=False)
    variant = Column(String(255), nullable=True)
    sku = Column(String(100), nullable=True)
    product_url = Column(Text, nullable=False)
    image_url = Column(Text, nullable=True)
    quantity = Column(Integer, default=1, nullable=False)
    paid_price = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    is_monitoring_active = Column(Boolean, default=True, nullable=False)
    monitoring_stopped_reason = Column(Enum(MonitoringStoppedReason), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    order = relationship("Order", back_populates="items")
    user = relationship("User")
    price_snapshots = relationship("PriceSnapshot", back_populates="order_item", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="order_item")
    outcome_logs = relationship("OutcomeLog", back_populates="order_item")

