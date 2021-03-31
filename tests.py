import pytest
import requests
import json
import datetime

URL = "http://0.0.0.0:8080"

@pytest.fixture
def positive_couriers_post_request_body():
    return json.dumps({
            "data": [
                    {
                    "courier_id": 1,
                    "courier_type": "foot",
                    "regions": [35],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                    },
                    {
                    "courier_id": 2,
                    "courier_type": "bike",
                    "regions": [22],
                    "working_hours": ["09:00-18:00"]
                    }]})


@pytest.fixture
def negative_couriers_post_request_body():
    return json.dumps({
            "data": [
                    {
                    "courier_id": 3,
                    "regions": [1, 12, 22],
                    "working_hours": ["11:35-14:05", "09:00-11:00"]
                    },
                    {
                    "courier_id": 4,
                    "courier_type": "",
                    "regions": [22],
                    "working_hours": ["09:00-18:00"]
                    },
                    {
                    "courier_id": 5,
                    "courier_type": "ApacheHelicopter",
                    "regions": [22],
                    "working_hours": ["09:00-18:00"]
                    },
                    {
                    "courier_id": 6,
                    "courier_type": "bike",
                    "regions": [],
                    "working_hours": ["09:00-18:00"]
                    },
                    {
                    "courier_id": 2,
                    "courier_type": "foot",
                    "regions": [22],
                    "working_hours": ["09:00-18:00"]
                    },
                    {
                    "courier_id": 7,
                    "courier_type": "car",
                    "regions": [22],
                    "working_hours": []
                    }
                    ]})


@pytest.fixture
def positive_orders_post_request_body():
    return json.dumps({
            "data": [
                    {
                    "order_id": 1,
                    "weight": 0.23,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"]
                    },
                    {
                    "order_id": 2,
                    "weight": 12,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"]
                    },
                    {
                    "order_id": 3,
                    "weight": 5,
                    "region": 22,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                    },
                    {
                    "order_id": 4,
                    "weight": 7,
                    "region": 22,
                    "delivery_hours": ["09:00-18:00"]
                    },
                    {
                    "order_id": 5,
                    "weight": 9,
                    "region": 22,
                    "delivery_hours": ["09:00-18:00"]
                    },
                    {
                    "order_id": 6,
                    "weight": 0.5,
                    "region": 22,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                    }]})


@pytest.fixture
def negative_orders_post_request_body():
    return json.dumps({
            "data": [
                    {
                    "order_id": 7,
                    "weight": -2,
                    "region": 12,
                    "delivery_hours": ["09:00-18:00"]
                    },
                    {
                    "order_id": 8,
                    "weight": 51,
                    "region": 1,
                    "delivery_hours": ["09:00-18:00"]
                    },
                    {
                    "order_id": 7,
                    "weight": 0.9,
                    "region": 22,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                    },
                    {
                    "order_id": 9,
                    "weight": 7,
                    "region": -4,
                    "delivery_hours": ["09:00-18:00"]
                    },
                    {
                    "order_id": 10,
                    "weight": 9,
                    "region": 22,
                    "delivery_hours": []
                    },
                    {
                    "order_id": 11,
                    "weight": 0.5,
                    "delivery_hours": ["09:00-12:00", "16:00-21:30"]
                    }]})


@pytest.fixture
def positive_courier_patch():
    return {"regions": [12]}


@pytest.fixture 
def negative_courier_patch():
    return {":D:DD": "man:D:DD"} 


@pytest.fixture
def positive_assign_order_post_request_body():
    return json.dumps({"courier_id": 2})


@pytest.fixture
def neutral_assign_order_post_request_body():
    return json.dumps({"courier_id": 1})


@pytest.fixture
def negative_assign_order_post_request_body():
    return json.dumps({"courier_id": 10040})


@pytest.fixture
def positive_order_patch_request_body(positive_courier_patch):
    return json.dumps(positive_courier_patch)


@pytest.fixture
def negative_order_patch_request_body(negative_courier_patch):
    return json.dumps(negative_courier_patch)


@pytest.fixture
def positive_complete_order_post_request_body():
    return json.dumps({"courier_id": 2, "order_id": 1, "complete_time": str(datetime.datetime.now())})


@pytest.fixture
def another_positive_complete_order_request_body(): 
    return json.dumps({"courier_id": 2, "order_id": 2, "complete_time": str(datetime.datetime.now())})


@pytest.fixture
def negative_complete_order_wrong_courier():
    return json.dumps({"courier_id": 1, "order_id": 2, "complete_time": str(datetime.datetime.now())})


@pytest.fixture
def negative_complete_order_no_such_order():
    return json.dumps({"courier_id": 2, "order_id": 15, "complete_time": str(datetime.datetime.now())})


def test_positive_courier_post_request(positive_couriers_post_request_body):
    post_response = requests.post(URL + "/couriers", data=positive_couriers_post_request_body)
    assert post_response.status_code == 201
    assert post_response.json()
    assert list(post_response.json().keys()) == ["couriers"]
    assert type(post_response.json()["couriers"]) == list
    assert all(type(post_response.json()["couriers"][i]) == dict for i in range(len(post_response.json()["couriers"])))


def test_negative_courier_post_request(negative_couriers_post_request_body):
    post_response = requests.post(URL + "/couriers", data=negative_couriers_post_request_body)
    assert post_response.status_code == 400
    assert post_response.json()
    assert list(post_response.json().keys()) == ["validation_error"]
    assert list(post_response.json()["validation_error"].keys()) == ["couriers"]
    assert all(type(post_response.json()["validation_error"]["couriers"][i]) == dict for i in range(len(post_response.json()["validation_error"]["couriers"])))


def test_positive_order_post_request(positive_orders_post_request_body):
    post_response = requests.post(URL + "/orders", data=positive_orders_post_request_body)
    assert post_response.status_code == 201
    assert post_response.json()
    assert list(post_response.json().keys()) == ["orders"]
    assert type(post_response.json()["orders"]) == list
    assert all(type(post_response.json()["orders"][i]) == dict for i in range(len(post_response.json()["orders"])))


def test_negative_order_post_request(negative_orders_post_request_body):
    post_response = requests.post(URL + "/orders", data=negative_orders_post_request_body)
    assert post_response.status_code == 400
    assert post_response.json()
    assert list(post_response.json().keys()) == ["validation_error"]
    assert list(post_response.json()["validation_error"].keys()) == ["orders"]
    assert all(type(post_response.json()["validation_error"]["orders"][i]) == dict for i in range(len(post_response.json()["validation_error"]["orders"])))


def test_positive_assign_post_request(positive_assign_order_post_request_body):
    post_response = requests.post(URL + "/orders/assign", data=positive_assign_order_post_request_body)
    assert post_response.status_code == 200
    assert list(post_response.json().keys()) == ["orders", "assign_time"]
    assert all(type(order) == dict for order in post_response.json()["orders"]) 
    assert post_response.json()["assign_time"]


def test_positive_assign_post_request_empty_response(neutral_assign_order_post_request_body):
    post_response = requests.post(URL + "/orders/assign", data=neutral_assign_order_post_request_body)
    assert post_response.status_code == 200
    assert list(post_response.json().keys()) == ["orders"]
    assert not post_response.json()["orders"]


def test_negative_assign_post_request(negative_assign_order_post_request_body):
    post_response = requests.post(URL + "/orders/assign", data=negative_assign_order_post_request_body)
    assert post_response.status_code == 400


def test_positive_courier_patch_request(positive_order_patch_request_body):
    patch_response = requests.patch(URL + f"/couriers/{2}", data=positive_order_patch_request_body)
    assert patch_response.status_code == 200
    assert len(patch_response.json().keys()) == 4
    assert set(patch_response.json().keys()) == {"courier_id", "courier_type", "regions", "working_hours"}
    assert json.loads(positive_order_patch_request_body)["regions"] == patch_response.json()["regions"]


def test_negative_courier_patch_request(negative_order_patch_request_body):
    patch_response = requests.patch(URL + f"/couriers/{2}", data=negative_order_patch_request_body)
    assert patch_response.status_code == 400


def test_second_order_assign(positive_assign_order_post_request_body):
    post_response = requests.post(URL + "/orders/assign", data=positive_assign_order_post_request_body)
    assert post_response.status_code == 200
    assert list(post_response.json().keys()) == ["orders", "assign_time"]
    assert all(type(order) == dict for order in post_response.json()["orders"]) 
    assert post_response.json()["assign_time"]


def test_positive_complete_order_post_request(positive_complete_order_post_request_body, another_positive_complete_order_request_body):
    post_response = requests.post(URL + "/orders/complete", data=positive_complete_order_post_request_body)
    assert post_response.status_code == 200
    assert list(post_response.json().keys()) == ["order_id"]
    another_post_response = requests.post(URL + "/orders/complete", data=another_positive_complete_order_request_body)
    assert another_post_response.status_code == 200
    assert list(another_post_response.json().keys()) == ["order_id"]


def test_negative_complete_order_wrong_courier(negative_complete_order_wrong_courier):
    post_response = requests.post(URL + "/orders/complete", data=negative_complete_order_wrong_courier)
    assert post_response.status_code == 400


def test_negative_complete_order_no_such_order(negative_complete_order_no_such_order):
    post_response = requests.post(URL + "/orders/complete", data=negative_complete_order_no_such_order)
    assert post_response.status_code == 400


def test_courier_stats_get_request():
    get_response = requests.get(URL + "/couriers/2")
    assert get_response.status_code == 200
    assert "rating" in get_response.json().keys() and "earnings" in get_response.json().keys()
    assert get_response.json()["rating"] and get_response.json()["earnings"]
