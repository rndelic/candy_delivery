from typing import List, Optional
from pydantic import BaseModel


class Courier(BaseModel):
    courier_id: Optional[int]
    courier_type: Optional[str]
    regions: Optional[List[int]]
    working_hours: Optional[List[str]]

    class Config:
        orm_mode = True


class CouriersListIn(BaseModel):
    data: List[Courier]


class CourierPatchIn(BaseModel):
    courier_type: Optional[str]
    regions: Optional[List[int]]
    working_hours: Optional[List[str]]


class Order(BaseModel):
    order_id: Optional[int]
    weight: Optional[float]
    region: Optional[int]
    delivery_hours: Optional[List[str]]

    class Config:
        orm_mode = True


class OrderListIn(BaseModel):
    data: List[Order]


class AssignedOrder(BaseModel):
    courier_id: int
    order_id: int
    assign_time: str

    class Config:
        orm_mode = True


class CourierAssignment(BaseModel):
    courier_id: int


class CompleteOrder(BaseModel):
    courier_id: int
    order_id: int
    complete_time: str
    region: Optional[int]
    courier_type: Optional[str]
    assign_time: Optional[str]

    class Config:
        orm_mode = True
