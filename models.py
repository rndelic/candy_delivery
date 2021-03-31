from sqlalchemy import Float, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class Courier(Base):
    __tablename__ = "couriers"

    courier_id = Column(Integer, primary_key=True)
    courier_type = Column(String)
    regions = Column(String)
    working_hours = Column(String)

    assigned_orders = relationship("AssignedOrder", back_populates="courier")
    complete_orders = relationship("CompleteOrder", back_populates="courier")


class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, index=True)
    weight = Column(Float, index=True)
    region = Column(Integer, index=True)
    delivery_hours = Column(Integer, index=True)

    complete_orders = relationship("CompleteOrder", back_populates="order")
    assigned_orders = relationship("AssignedOrder", back_populates="order")


class CompleteOrder(Base):
    __tablename__ = "complete_orders"
    
    id = Column(Integer, primary_key=True, index=True)
    courier_id = Column(Integer, ForeignKey("couriers.courier_id"))
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    complete_time = Column(String)
    region = Column(Integer)
    courier_type = Column(String)
    assign_time = Column(String)

    courier = relationship("Courier", back_populates="complete_orders")
    order = relationship("Order", back_populates="complete_orders")


class AssignedOrder(Base):
    __tablename__ = "assigned_orders"

    id = Column(Integer, primary_key=True, index=True) 
    courier_id = Column(Integer, ForeignKey("couriers.courier_id"))
    order_id = Column(Integer, ForeignKey("orders.order_id"))
    assign_time = Column(String)

    courier = relationship("Courier", back_populates="assigned_orders")
    order = relationship("Order", back_populates="assigned_orders")

