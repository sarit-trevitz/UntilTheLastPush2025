from sqlalchemy import create_engine, Column, String, Integer, Float, ForeignKey, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

from datetime import datetime

# import os
# if os.path.exists("health_monitor.db"):
#     os.remove("health_monitor.db")


# הגדרת בסיס
Base = declarative_base()

# טבלת משתמשים
class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)  # national_id
    first_name = Column(String)
    last_name = Column(String)
    sensor_data = relationship("SensorData", back_populates="user", cascade="all, delete-orphan")
    exceptions = relationship("ExceptionLog", back_populates="user", cascade="all, delete-orphan")

# טבלת מדדים
class SensorData(Base):
    __tablename__ = 'sensor_data'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    timestamp = Column(String, default=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    heart_rate = Column(Integer)
    temperature = Column(Float)
    movement_level = Column(Float)
    sweat_level = Column(Float)

    user = relationship("User", back_populates="sensor_data")

# טבלת חריגות
class ExceptionLog(Base):
    __tablename__ = 'exception'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(String, default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    details = Column(String, nullable=False)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    exception_type = Column(String, nullable=False)
    exception_level = Column(String, nullable=False)

    user = relationship("User", back_populates="exceptions")

    __table_args__ = (
        CheckConstraint(
            "exception_type IN ('fall', 'heatstroke', 'coldshock', 'dehydration', 'pre_syncope', 'heart_attack')",
            name='valid_exception_type'
        ),
        CheckConstraint(
            "exception_level IN ('green', 'orange', 'red')",
            name='valid_exception_level'
        ),
    )

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

def get_sensor_data_from_date(start_date: str):
    sensor_data = session.query(SensorData).filter(SensorData.timestamp >= start_date).all()
    return [
        {
            "id": d.id,
            "user_id": d.user_id,
            "timestamp": d.timestamp,
            "heart_rate": d.heart_rate,
            "temperature": d.temperature,
            "movement_level": d.movement_level,
            "sweat_level": d.sweat_level
        }
        for d in sensor_data
    ]


def delete_sensor_record(record_id: int):
    record = session.query(SensorData).filter_by(id=record_id).first()
    if record:
        session.delete(record)
        session.commit()
        return {"message": "Record deleted"}
    return {"error": "Record not found"}

# --- Excepetion CRUD ---

def add_exception(user_id: str, exception_type: str, exception_level: str, details: str, timestamp: str = None):
    if not session.query(User).filter_by(id=user_id).first():
        return {"error": "User does not exist"}

    if timestamp is None:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    exception = ExceptionLog(
        user_id=user_id,
        exception_type=exception_type,
        exception_level=exception_level,
        details=details,
        timestamp=timestamp
    )
    session.add(exception)
    session.commit()
    return {"message": "Exception added", "exception_id": exception.id}

def get_all_exceptions():
    exceptions = session.query(ExceptionLog).all()
    return [
        {
            "id": e.id,
            "user_id": e.user_id,
            "timestamp": e.timestamp,
            "exception_type": e.exception_type,
            "exception_level": e.exception_level,
            "details": e.details,
        }
        for e in exceptions
    ]



def delete_exception(exception_id: int):
    exception = session.query(ExceptionLog).filter_by(id=exception_id).first()
    if exception:
        session.delete(exception)
        session.commit()
        return {"message": "Exception deleted"}
    return {"error": "Exception not found"}



def get_latest_exception_timestamp():
    latest = session.query(ExceptionLog).order_by(ExceptionLog.timestamp.desc()).first()
    if latest:
        return latest.timestamp
    return None


def get_exceptions_from_date(start_date: str):
    exceptions = session.query(ExceptionLog).filter(ExceptionLog.timestamp >= start_date).all()
    return [
        {
            "id": e.id,
            "user_id": e.user_id,
            "timestamp": e.timestamp,
            "exception_type": e.exception_type,
            "exception_level": e.exception_level,
            "details": e.details,
        }
        for e in exceptions
    ]



