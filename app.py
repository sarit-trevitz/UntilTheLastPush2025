from fastapi import FastAPI, HTTPException, Query
import numpy as np
from pydantic import BaseModel
import random
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

from model import (
    add_user,
    get_last_sensor_data_by_user,
    get_last_exception_from_date,
    get_user,
    delete_user,
    add_sensor_data,
    delete_sensor_record,
    get_latest_exception_timestamp,
    get_all_users,
)

from check import check_all_conditions
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


NUM_OF_RECORDS = 1000  # מספר רשומות לדוגמה
USER_ID = "1"  # מזהה משתמש
emergency: datetime | None = None

# ----------- MODELS FOR REQUESTS ----------- #
class UserCreate(BaseModel):
    id: str
    first_name: str
    last_name: str


class SensorDataCreate(BaseModel):
    heart_rate: int
    temperature: float
    movement_x: float
    movement_y: float
    movement_z: float
    sweat_level: float


def emergency_on() -> bool:
    """
    Check if the emergency button is pressed.
    """
    global emergency
    if emergency is None:
        return False
    return emergency > datetime.now() - timedelta(seconds=10)



@app.delete("/emergency")
def emergency_status():
    global emergency
    emergency = None
    return {"status": emergency_on()}


@app.get("/emergency")
def emergency_status():
    global emergency
    return {"status": emergency_on()}


@app.post("/emergency")
def emergency_status():
    global emergency
    emergency = datetime.now()
    return {"status": emergency_on()}


# ----------- USER ENDPOINTS ----------- #
@app.post("/users")
def create_user(user: UserCreate):
    result = add_user(user.id, user.first_name, user.last_name)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.get("/users/{user_id}")
def read_user(user_id: str):
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"id": user.id, "first_name": user.first_name, "last_name": user.last_name}


@app.get("/users/")
def all_users():
    return get_all_users()


@app.delete("/users/{user_id}")
def remove_user(user_id: str):
    result = delete_user(user_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ----------- SENSOR DATA ENDPOINTS ----------- #
# חיבור עם החומרה
@app.post("/users/{user_id}/metrics")
def create_sensor_data(user_id: str, data: SensorDataCreate):
    result = add_sensor_data(user_id, data.model_dump())
    # Check exceptions for user id  check_for_user_id(user_id)
    check_all_conditions(user_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # Wrtie to db exception with the current timestamp
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.get("/buzz")
def buzz():
    reference_date = get_latest_exception_timestamp()
    if reference_date is None:
        return {"status": False}
    return {"status": reference_date > datetime.now() - timedelta(seconds=5)}


@app.get("/test")
def check_date(
    date_str: str = Query(
        default=None,
        description="Date in format YYYY-MM-DDTHH:MM:SS (default: current time)"
    )
):
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    reference_date = get_latest_exception_timestamp()
    if reference_date is None:
        return JSONResponse(status_code=201, content={"error": "No exceptions found on the system"})

    try:
        if isinstance(date_str, str) and "T" in date_str:
            date_str = date_str.replace("T", " ")  # תומך ב-T או רווח
        input_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return JSONResponse(
            status_code=400, content={"error": f"Got '{date_str}', Invalid date format. Use YYYY-MM-DD HH:MM:SS or YYYY-MM-DDTHH:MM:SS"}
        )

    if input_date < reference_date:
        new = get_last_exception_from_date(date_str)  # השתמש בתאריך שנוקה
        if new is not None and "user_id" in new:
            user_id = new["user_id"]
            new["user"] = get_user(user_id)
        return {"res": "before", "new_data": new}
    return {"res": "after"}


@app.delete("/metrics/{record_id}")
def delete_metric_record(record_id: int):
    result = delete_sensor_record(record_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.get("/metrics/last/{user_id}")
def get_last_metric(user_id: str):
    result = get_last_sensor_data_by_user(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="No metrics found")
    return result


# ----------- DEMO UTILITIES ----------- #
def random_metric():
    return SensorDataCreate(
        heart_rate=random.randint(60, 110),
        temperature=round(random.uniform(36.0, 38.5), 1),
        movement_x=round(random.uniform(0.0, 1.0), 2),
        movement_y=round(random.uniform(0.0, 1.0), 2),
        movement_z=round(random.uniform(0.0, 1.0), 2),
        sweat_level=round(random.uniform(0.0, 1.0), 2),
    )


def random_datetime():
    now = datetime.now()
    return now - timedelta(minutes=random.randint(0, 60 * 24 * 3))  # up to 3 days ago


@app.get("/demo")
def generate_demo():
    demo_user = UserCreate(id="1", first_name="Demo", last_name="User")
    add_user(demo_user.id, demo_user.first_name, demo_user.last_name)

    start_time = datetime.now()

    for i in range(NUM_OF_RECORDS):
        heart_rate = int(np.random.normal(loc=85, scale=15))
        temperature = 30 + (12 * i / NUM_OF_RECORDS)  # Gradually increase temperature from 30 to 42
        sweat_level = round(np.random.normal(loc=0.5, scale=0.2), 2)
        movement_x = round(np.random.normal(loc=0.5, scale=0.2), 2)
        movement_y = round(np.random.normal(loc=0.5, scale=0.2), 2)
        movement_z = round(np.random.normal(loc=0.5, scale=0.2), 2)

        timestamp = start_time + timedelta(seconds=i)  # Increment by 1 second for each record

        data = {
            "heart_rate": max(25, min(150, heart_rate)),
            "temperature": temperature,
            "movement_x": max(0, min(1, movement_x)),
            "movement_y": max(0, min(1, movement_y)),
            "movement_z": max(0, min(1, movement_z)),
            "sweat_level": max(0, min(1, sweat_level)),
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }

        add_sensor_data(USER_ID, data)
        check_all_conditions(USER_ID, timestamp.strftime("%Y-%m-%d %H:%M:%S"))

    return {"info": f"Created {NUM_OF_RECORDS} demo records for user 1 with high temperature to trigger exceptions"}
