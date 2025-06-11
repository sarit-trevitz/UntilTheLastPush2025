from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# הגדרת בסיס
Base = declarative_base()

# טבלת משתמשים
class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)  # national_id
    first_name = Column(String)
    last_name = Column(String)

    sensor_data = relationship("SensorData", back_populates="user", cascade="all, delete-orphan")

# טבלת מדדים
class SensorData(Base):
    __tablename__ = 'sensor_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    heart_rate = Column(Integer)
    temperature = Column(Float)
    movement_level = Column(Float)
    blood_oxygen = Column(Float)
    sweat_level = Column(Float)

    user = relationship("User", back_populates="sensor_data")

# יצירת חיבור למסד הנתונים
engine = create_engine('sqlite:///health_monitor.db')
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

# ==================== פונקציות CRUD ====================

# --- User CRUD ---

def add_user(user_id: str, first_name: str, last_name: str):
    if session.query(User).filter_by(id=user_id).first():
        return {"error": "User already exists"}
    user = User(id=user_id, first_name=first_name, last_name=last_name)
    session.add(user)
    session.commit()
    return {"message": "User added successfully"}

def get_user(user_id: str):
    return session.query(User).filter_by(id=user_id).first()

def delete_user(user_id: str):
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        session.delete(user)
        session.commit()
        return {"message": "User deleted"}
    return {"error": "User not found"}

# --- SensorData CRUD ---

def add_sensor_data(user_id: str, data: dict):
    if not session.query(User).filter_by(id=user_id).first():
        return {"error": "User does not exist"}
    record = SensorData(user_id=user_id, **data)
    session.add(record)
    session.commit()
    return {"message": "Sensor data added", "record_id": record.id}

def get_all_sensor_data(user_id: str):
    user = session.query(User).filter_by(id=user_id).first()
    if not user:
        return {"error": "User not found"}
    return [
        {
            "id": d.id,
            "heart_rate": d.heart_rate,
            "temperature": d.temperature,
            "movement_level": d.movement_level,
            "blood_oxygen": d.blood_oxygen,
            "sweat_level": d.sweat_level,
        }
        for d in user.sensor_data
    ]

def delete_sensor_record(record_id: int):
    record = session.query(SensorData).filter_by(id=record_id).first()
    if record:
        session.delete(record)
        session.commit()
        return {"message": "Record deleted"}
    return {"error": "Record not found"}

# ==================== דוגמה להפעלה מקומית ====================
if __name__ == "__main__":
    add_user("123456789", "Noa", "Nissim")

    add_sensor_data("123456789", {
        "heart_rate": 90,
        "temperature": 37.3,
        "movement_level": 0.2,
        "blood_oxygen": 98.1,
        "sweat_level": 0.5
    })

    print(get_all_sensor_data("123456789"))
