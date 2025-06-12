from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import random
from datetime import datetime, timedelta
from fastapi.responses import JSONResponse

from model import (
    add_user, get_user, delete_user,
    add_sensor_data, delete_sensor_record
    , get_latest_exception_timestamp, get_exceptions_from_date
)

from check import (
    check_all_conditions
)

app = FastAPI()

# ----------- MODELS FOR REQUESTS ----------- #
class UserCreate(BaseModel):
    id: str
    first_name: str
    last_name: str

class SensorDataCreate(BaseModel):
    heart_rate: int
    temperature: float
    movement_level: float
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
    exeptions = check_all_conditions(user_id)
     # Wrtie to db exception with the current timestamp
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.get("/test/{date_str}")
def check_date(date_str: str):
    # Define the reference date
    reference_date = get_latest_exception_timestamp()
    
    try:
        input_date = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return JSONResponse(status_code=400, content={"error": "Invalid date format. Use YYYY-MM-DD HH:MM:SS"})
    
    if input_date < reference_date:
        new = get_exceptions_from_date( date_str)
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
        blood_oxygen=round(random.uniform(94.0, 99.9), 1),
        sweat_level=round(random.uniform(0.0, 1.0), 2)
    )

def random_datetime():
    now = datetime.now()
    return now - timedelta(minutes=random.randint(0, 60*24*3))  # up to 3 days ago

@app.post("/demo")
def generate_demo():
    demo_user = UserCreate(id="999999999", first_name="Demo", last_name="User")
    user_result = add_user(demo_user.id, demo_user.first_name, demo_user.last_name)
    if "error" in user_result:
        return {"info": "Demo user already exists"}

    for _ in range(5):
        metric = random_metric()
        add_sensor_data(demo_user.id, metric.model_dump())
    return {"info": "Demo user and sample metrics created."}
