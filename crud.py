from sqlalchemy.orm import Session
from fastapi import HTTPException
import models
import schemas
import ast 
import datetime
import pandas as pd


def get_courier_by_id(db: Session, courier_id: int):
    courier = db.query(models.Courier).filter(models.Courier.courier_id == courier_id).first()
    return courier 


def get_all_couriers(db: Session):
    return db.query(models.Courier).all()


def create_couriers(db: Session, courier_list: schemas.CouriersListIn, success_list: list):
    for courier in courier_list.data:
        courier = models.Courier(courier_id=courier.courier_id, courier_type=courier.courier_type, 
                                 regions=str(courier.regions), working_hours=str(courier.working_hours))
        db.add(courier)
        db.commit()
        db.refresh(courier)
    return {"couriers": success_list}


def update_courier(db: Session, courier_id: int, patch_info: schemas.CourierPatchIn):
    previous_courier_data = get_courier_by_id(db=db, courier_id=courier_id)
    courier_orders = get_assigned_orders_by_courier(db=db, courier_id=courier_id)
    current_weight_on_courier = 0
    if courier_orders:
        for order in courier_orders:
            order = get_order_by_id(db=db, order_id=order.order_id) 
            current_weight_on_courier += order.weight
    
    #Если изменилась грузоподъемность
    if patch_info.courier_type is not None:
        weight_map = {"foot": 10.0, "bike": 15.0, "car": 50}
        new_courier_capacity = weight_map[patch_info.courier_type]
        #Если новая грузоподъемность меньше старой
        if new_courier_capacity < weight_map[previous_courier_data.courier_type]:
            #Удаляем назначенные заказы, пока суммарный вес текущих заказов больше новой грузоподъемности
            for order in courier_orders:
                order = get_order_by_id(db=db, order_id=order.order_id)
                db.query(models.AssignedOrder).filter(models.AssignedOrder.order_id == order.order_id).delete()
                current_weight_on_courier -= order.weight
                if current_weight_on_courier < new_courier_capacity:
                    break
        db.query(models.Courier).filter(models.Courier.courier_id == courier_id).update({models.Courier.courier_type: str(patch_info.courier_type)})
    
    #Если изменились регионы
    if patch_info.regions is not None:
        #Удаляем назначенные заказы из регионов, не входящих в новый список
        for order in courier_orders:
            order = get_order_by_id(db=db, order_id=order.order_id)
            if order.region not in patch_info.regions:
                db.query(models.AssignedOrder).filter(models.AssignedOrder.order_id == order.order_id).delete()
        db.query(models.Courier).filter(models.Courier.courier_id == courier_id).update({models.Courier.regions: str(patch_info.regions)})
    
    #Если изменился график
    if patch_info.working_hours is not None:
        #Удаляем назначенные заказы с неподходящими часами приема
        for order in courier_orders:
            order = get_order_by_id(db=db, order_id=order.order_id)
            time_suited = False
            for delivery_period in ast.literal_eval(order.delivery_hours):
                for work_period in patch_info.working_hours:
                    if datetime.time(int(delivery_period[:2]), int(delivery_period[3:5])) < datetime.time(int(work_period[-5:-3]), int(work_period[-2:])) \
                            or datetime.time(int(delivery_period[-5:-3]), int(delivery_period[-2:])) > datetime.time(int(work_period[:2]), int(work_period[3:5])):
                                time_suited = True
                                break
                if time_suited:
                    break
            if not time_suited:
                db.query(models.AssignedOrder).filter(models.AssignedOrder.order_id == order.order_id).delete()
        db.query(models.Courier).filter(models.Courier.courier_id == courier_id).update({models.Courier.working_hours: str(patch_info.working_hours)})
    db.commit()
    courier = get_courier_by_id(db=db, courier_id=courier_id)
    courier.regions = ast.literal_eval(courier.regions)
    courier.working_hours = ast.literal_eval(courier.working_hours)
    return courier


def get_order_by_id(db: Session, order_id: int):
    order = db.query(models.Order).filter(models.Order.order_id == order_id).first()
    return order


def get_all_orders(db: Session):
    return db.query(models.Order).all()


def create_orders(db: Session, order_list: schemas.OrderListIn, success_list: list):
    for order in order_list.data:
        order = models.Order(order_id=order.order_id, weight=order.weight, region=order.region, delivery_hours=str(order.delivery_hours))
        db.add(order)
        db.commit()
        db.refresh(order)
    return {"orders": success_list}


def assign_orders(db: Session, courier_id: int):
    #Берем все добавленные, назначенные, выполненные заказы  
    assigned_orders = {order.order_id for order in get_all_assigned_orders(db=db)}
    all_orders = {order.order_id for order in get_all_orders(db=db)}
    complete_orders = {order.order_id for order in get_all_complete_orders(db=db)}
    #Получаем невыполненные 
    unassigned_orders = all_orders - assigned_orders 
    unassigned_orders = [get_order_by_id(db=db, order_id=order) for order in unassigned_orders]
    #Будем назначать задачи жадно: от самых тяжелых до самых легких. Исходим из предположения, что тяжелее=ценнее (хотя в общем случае это не так, и нам понадобится цена, чтобы решить задачу о рюкзаке :) )
    unassigned_orders.sort(key=lambda x: x.weight, reverse=True)

    courier = get_courier_by_id(db=db, courier_id=courier_id)
    weight_map = {"foot": 10.0, "bike": 15.0, "car": 50.0}
    courier_capacity = weight_map[courier.courier_type]
    current_weight_on_courier = 0
    courier_assigned_orders = get_assigned_orders_by_courier(db=db, courier_id=courier_id)
    assignment_list = []
    #Считаем, сколько на курьере на данный момент веса (если на нем есть заказы)
    if courier_assigned_orders:
        for order in courier_assigned_orders:
            current_weight_on_courier += get_order_by_id(db=db, order_id=order.order_id).weight
    #Проверяем каждый заказ из неназначенных 
    for order in unassigned_orders:
        time_suited = False
        #Проверяем, пересекается ли хотя бы один интервал приема заказа с хотя бы одним интервалом работы
        for delivery_period in ast.literal_eval(order.delivery_hours):
            for work_period in ast.literal_eval(courier.working_hours):
                if datetime.time(int(delivery_period[:2]), int(delivery_period[3:5])) < datetime.time(int(work_period[-5:-3]), int(work_period[-2:])) \
                or datetime.time(int(delivery_period[-5:-3]), int(delivery_period[-2:])) > datetime.time(int(work_period[:2]), int(work_period[3:5])):
                    time_suited = True
                    break
            if time_suited:
                break
        #Если курьер вместит заказ, работает в подходящем регионе и в подходящие часы - назначаем на него заказ
        if current_weight_on_courier + order.weight <= courier_capacity and order.region in ast.literal_eval(courier.regions) and time_suited and order.order_id not in complete_orders:
            current_weight_on_courier += order.weight
            order = models.AssignedOrder(order_id=order.order_id, courier_id=courier.courier_id, assign_time=str(datetime.datetime.now()))
            db.add(order)
            assignment_list.append({"id": order.order_id})
    if assignment_list:
        db.commit()
        return {"orders": assignment_list, "assign_time": str(datetime.datetime.now())}
    else:
        return {"orders": []}


def complete_order(db: Session, complete_order: schemas.CompleteOrder):
    assigned_order = get_assigned_order(db=db, order_id=complete_order.order_id)
    order = get_order_by_id(db=db, order_id=complete_order.order_id)
    courier = get_courier_by_id(db=db, courier_id=complete_order.courier_id)

    if assigned_order and order and assigned_order.courier_id == complete_order.courier_id:
        complete_order = models.CompleteOrder(order_id=complete_order.order_id, courier_id=complete_order.courier_id, complete_time=complete_order.complete_time,
                                              region=order.region, courier_type=courier.courier_type, assign_time=assigned_order.assign_time)
        db.add(complete_order)
        db.commit()
        db.refresh(complete_order)
        return {"order_id": complete_order.order_id}
    else:
        raise HTTPException(status_code=400, detail="Bad Request")


def get_courier_stats(db: Session, courier_id: int):
    complete_orders = get_complete_orders_by_courier(db=db, courier_id=courier_id)
    courier = get_courier_by_id(db=db, courier_id=courier_id)
    if complete_orders:
        stats_table = pd.DataFrame()
        for i, complete_order in enumerate(complete_orders):
            order_dict = {"courier_id": complete_order.courier_id,
                          "order_id": complete_order.order_id,
                          "complete_time": complete_order.complete_time,
                          "region": complete_order.region,
                          "courier_type": complete_order.courier_type,
                          "assign_time": complete_order.assign_time}
            stats_table = stats_table.append(pd.DataFrame(order_dict, index=pd.Index([i])))
        
        stats_table['complete_time'] = pd.to_datetime(stats_table['complete_time'])
        stats_table['assign_time'] = pd.to_datetime(stats_table['assign_time'])
        stats_table['delivery_time'] = (stats_table['complete_time'] - stats_table['complete_time'].shift(1)).dt.seconds
        stats_table['delivery_time'].loc[0] = (stats_table['complete_time'].loc[0] - stats_table['assign_time'].loc[0]).seconds

        magic_t = stats_table.groupby('region').mean().delivery_time.min()
        rating = round((60*60 - min(magic_t, 3600)) / (60*60) * 5, 2)
        
        coefficient_map = {"foot": 2, "bike": 5, "car": 9}
        stats_table.courier_type = stats_table.courier_type.map(coefficient_map)
        earnings = sum(stats_table.courier_type * 500)
        
        stats_response = {"courier_id": courier_id, "courier_type": courier.courier_type, "regions": ast.literal_eval(courier.regions),
                          "working_hours": ast.literal_eval(courier.working_hours), "rating": rating, "earnings": earnings} 
        return stats_response
    else:
        return courier


def get_all_assigned_orders(db: Session):
    return db.query(models.AssignedOrder).all()


def get_assigned_orders_by_courier(db: Session, courier_id: int):
    return db.query(models.AssignedOrder).filter(models.AssignedOrder.courier_id == courier_id).all()


def get_assigned_order(db: Session, order_id: int):
    return db.query(models.AssignedOrder).filter(models.AssignedOrder.order_id == order_id).first()


def get_all_complete_orders(db: Session):
    return db.query(models.CompleteOrder).all()


def get_complete_orders_by_courier(db: Session, courier_id: int):
    return db.query(models.CompleteOrder).filter(models.CompleteOrder.courier_id == courier_id).all()
