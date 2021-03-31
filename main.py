from typing import List

from fastapi import Depends, FastAPI, status, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import SessionLocal, engine
import crud
import models
import schemas


models.Base.metadata.create_all(bind=engine)


class InvalidCourierException(Exception):
    def __init__(self, errors: list):
        self.errors = errors


class InvalidOrderException(Exception):
    def __init__(self, errors: list):
        self.errors = errors


app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.exception_handler(InvalidCourierException)
async def invalid_courier_exception_handler(request: Request, exc: InvalidCourierException):
    return JSONResponse(
        status_code=400,
        content={"validation_error": {"couriers": exc.errors}}
    )


@app.exception_handler(InvalidOrderException)
async def invalid_order_exception_handler(request: Request, exc: InvalidOrderException):
    return JSONResponse(
            status_code=400,
            content={"validation_error": {"orders": exc.errors}}
        )


@app.post("/couriers", status_code=status.HTTP_201_CREATED)
async def create_courier(courier_list: schemas.CouriersListIn, db: Session = Depends(get_db)):
    error_list = []
    success_list = []
    for courier in courier_list.data:
        if all(courier.dict().values()) and not crud.get_courier_by_id(db=db, courier_id=courier.courier_id) and courier.courier_type in ["foot", "bike", "car"] and all(region > 0 for region in courier.regions):
           success_list.append({"id": courier.courier_id})
        else:
            error_list.append({"id": courier.courier_id})
    if not error_list:
        return crud.create_couriers(db=db, courier_list=courier_list, success_list=success_list)
    else: 
        raise InvalidCourierException(errors=error_list)


@app.patch("/couriers/{courier_id}", status_code=status.HTTP_200_OK)
async def update_courier(courier_id: int, patch_info: schemas.CourierPatchIn, db: Session = Depends(get_db)):
    if not any(patch_info.dict().values()):
        raise HTTPException(status_code=400, detail="Bad Request")
    else:
        return crud.update_courier(db=db, courier_id=courier_id, patch_info=patch_info) 


@app.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_order(order_list: schemas.OrderListIn, db: Session = Depends(get_db)):
    error_list = []
    success_list = []
    for order in order_list.data:
        if all(order.dict().values()) and not crud.get_order_by_id(db=db, order_id=order.order_id) and order.weight >= 0.01 and order.weight <= 50 and order.region > 0:
            success_list.append({"id": order.order_id})
        else:
            error_list.append({"id": order.order_id})
    if not error_list:
        return crud.create_orders(db=db, order_list=order_list, success_list=success_list)
    else:
        raise InvalidOrderException(errors=error_list)


@app.post("/orders/assign", status_code=status.HTTP_200_OK)
async def assign_orders(courier_assignment: schemas.CourierAssignment, db: Session = Depends(get_db)):
    if not crud.get_courier_by_id(db=db, courier_id=courier_assignment.courier_id):
        raise HTTPException(status_code=400, detail="Bad Request")
    else:
        return crud.assign_orders(db=db, courier_id=courier_assignment.courier_id)


@app.post("/orders/complete", status_code=status.HTTP_200_OK)
async def complete_order(complete_order: schemas.CompleteOrder, db: Session = Depends(get_db)):
    return crud.complete_order(db=db, complete_order=complete_order)


@app.get("/couriers/{courier_id}", status_code=status.HTTP_200_OK)
async def get_courier_stats(courier_id: int, db: Session = Depends(get_db)):
    return crud.get_courier_stats(db=db, courier_id=courier_id)
