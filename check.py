from model import (
    add_user, get_user, delete_user,
    add_sensor_data, get_all_sensor_data, delete_sensor_record,
    add_exception, get_all_exceptions, delete_exception
)

def check_all_conditions(user_id: str, timestamp: str):
    detect_fall(user_id, timestamp)
    detect_heatstroke(user_id, timestamp)
    detect_hypothermia(user_id, timestamp)
    detect_dehydration(user_id, timestamp)
    detect_presyncope(user_id, timestamp)


from datetime import datetime

def add_exception_helper(user_id: str, exception_type: str, exception_level: str, details: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        add_exception(user_id, exception_type, exception_level, details, timestamp)
