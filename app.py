from fastapi import FastAPI, HTTPException, Query
import numpy as np
from pydantic import BaseModel
from typing import List
import random
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

from model import (
    add_user, get_last_exception_from_date, get_user, delete_user,
    add_sensor_data, delete_sensor_record
    , get_latest_exception_timestamp, get_all_users
)

from check import (
    check_all_conditions
)

app = FastAPI()

NUM_OF_RECORDS = 1000  # מספר רשומות לדוגמה
USER_ID = "1"  # מזהה משתמש

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
    #exeptions = check_all_conditions(user_id)
     # Wrtie to db exception with the current timestamp
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.get("/test")
def check_date(date_str: str = Query(..., description="Date in format YYYY-MM-DDTHH:MM:SS")):
    reference_date = get_latest_exception_timestamp()
    if reference_date is None:
        return JSONResponse(
            status_code=201,
            content={"error": "No reference timestamp found in the system"}
        )

    try:
        cleaned_date = date_str.replace("T", " ")  # תומך ב-T או רווח
        input_date = datetime.strptime(cleaned_date, "%Y-%m-%d %H:%M:%S")
        print(f"Input date: {input_date}, Reference date: {reference_date}")
    except ValueError:
        return JSONResponse(
            status_code=400,
            content={"error": "Invalid date format. Use YYYY-MM-DD HH:MM:SS or YYYY-MM-DDTHH:MM:SS"}
        )

    if input_date < reference_date:
        new = get_last_exception_from_date(cleaned_date)  # השתמש בתאריך שנוקה
        if new is not None and "user_id" in new:
            user_id = new["user_id"]
            new["user"] = get_user(user_id)
        return {"res": "before", "new_data": new}
    else:
        return {"res": "after"}

@app.delete("/metrics/{record_id}")
def delete_metric_record(record_id: int):
    result = delete_sensor_record(record_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


# ----------- DEMO UTILITIES ----------- #
def random_metric():
    return SensorDataCreate(
        heart_rate=random.randint(60, 110),
        temperature=round(random.uniform(36.0, 38.5), 1),
        movement_level=round(random.uniform(0.0, 1.0), 2),
        sweat_level=round(random.uniform(0.0, 1.0), 2)
    )

def random_datetime():
    now = datetime.now()
    return now - timedelta(minutes=random.randint(0, 60*24*3))  # up to 3 days ago

@app.post("/demo")
def generate_demo():
    demo_user = UserCreate(id=1, first_name="Demo", last_name="User")
    user_result = add_user(demo_user.id, demo_user.first_name, demo_user.last_name)
    if "error" in user_result:
        return {"info": "Demo user already exists"}

    start_time = datetime.now()

    for i in range(NUM_OF_RECORDS):
        heart_rate = int(np.random.normal(loc=85, scale=15))
        temperature = round(np.random.normal(loc=37.0, scale=1.0), 1)
        sweat_level = round(np.random.normal(loc=0.5, scale=0.2), 2)

        movement_x = round(np.random.normal(loc=0.5, scale=0.2), 2)
        movement_y = round(np.random.normal(loc=0.5, scale=0.2), 2)
        movement_z = round(np.random.normal(loc=0.5, scale=0.2), 2)

        timestamp = start_time + timedelta(seconds=random.randint(0, 3 * 24 * 60 * 60))
        # timestamp = datetime.now() - timedelta(seconds=random.randint(0, 3 * 24 * 60 * 60))  # אקראי עד 3 ימים אחורה


        data = {
            "heart_rate": max(25, min(150, heart_rate)),
            "temperature": max(35, min(41, temperature)),
            "movement_x": max(0, min(1, movement_x)),
            "movement_y": max(0, min(1, movement_y)),
            "movement_z": max(0, min(1, movement_z)),
            "sweat_level": max(0, min(1, sweat_level)),
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

        add_sensor_data(USER_ID, data)

    return {"info": f"Created {NUM_OF_RECORDS} demo records for user 1"}
    # generate_mock_data()

    # for _ in range(5):
    #     metric = random_metric()
    #     add_sensor_data(demo_user.id, metric.model_dump())
    # return {"info": "Demo user and sample metrics created."}
