from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# מודל לקליטת נתונים
class SensorData(BaseModel):
    soldier_id: str
    heart_rate: int
    temperature: float
    movement_level: float
    blood_oxygen: float
    sweat_level: float

# נקודת קלט
@app.post("/data")
def receive_data(data: SensorData):
    print("📡 קיבלנו נתונים:", data)
    return {"status": "success", "received": data}
