from model import (
    add_user, get_user, delete_user,
    add_sensor_data, get_all_sensor_data, delete_sensor_record
)

def check_all_conditions(user_id: str, timestamp: str):
    detect_fall(user_id, timestamp)
    detect_heatstroke(user_id, timestamp)
    detect_hypothermia(user_id, timestamp)
    detect_dehydration(user_id, timestamp)
    detect_presyncope(user_id, timestamp)

