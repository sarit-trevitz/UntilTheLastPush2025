from model import (
    add_user, get_user, delete_user,
    delete_sensor_record,
    add_exception, get_all_exceptions, delete_exception, get_sensor_data_from_date
)

from datetime import datetime, timedelta
from model import add_exception

def check_all_conditions(user_id: str, timestamp: str):
    # detect_fall(user_id, timestamp)
    # detect_heatstroke(user_id, timestamp)
    # detect_hypothermia(user_id, timestamp)
    # detect_dehydration(user_id, timestamp)
    # detect_presyncope(user_id, timestamp)
    #analyze_temperature_critical_from_db(user_id, timestamp)
    pass



def add_exception_helper(user_id: str, exception_type: str, exception_level: str, details: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        add_exception(user_id, exception_type, exception_level, details, timestamp)



# temperature_analysis.py\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\


def analyze_temperature_critical(data_rows, user_id):
    """
    Detects heat-related and hypothermia-related temperature anomalies over time.
    Assumes 2-second sampling. Each row: (timestamp, heart_rate, temperature, movement_level, sweat_level)
    """
    alerts = []

    for i in range(300, len(data_rows)):  # Require at least 10 minutes of data
        ts, hr, temp, move, sweat = data_rows[i]
        window_10min = data_rows[i-299:i+1]

        # Mild fever: 37.6–38.0°C for 10+ minutes
        if all(37.6 <= r[2] <= 38.0 for r in window_10min):
            alerts.append(("mild_fever", "orange", "Mild fever lasting over 10 minutes"))

        # Moderate fever: 38.1–39.0°C
        if 38.1 <= temp <= 39.0:
            if hr > 150:
                alerts.append(("heatstroke_risk", "red", f"Temp {temp}°C + HR {hr} – CRITICAL heat overload"))
            else:
                alerts.append(("moderate_fever", "orange", f"Moderate fever {temp}°C – possible overload"))

        # High fever: above 39.0°C
        if temp > 39.0:
            alerts.append(("heatstroke", "red", f"High fever {temp}°C – IMMEDIATE danger"))

        # Mild cooling: 35.5–36.0°C for 10+ minutes
        if all(35.5 <= r[2] <= 36.0 for r in window_10min):
            alerts.append(("mild_cooling", "orange", "Body temp low (35.5–36.0°C) for 10+ min"))

        # Mild hypothermia: 35.0–35.4°C
        if 35.0 <= temp < 35.5:
            alerts.append(("mild_hypothermia", "red", f"Mild hypothermia {temp}°C – monitor closely"))

        # Severe hypothermia: below 35.0°C
        if temp < 35.0:
            alerts.append(("severe_hypothermia", "red", f"Severe hypothermia {temp}°C – CRITICAL"))

    # Store alerts in the database
    for etype, level, details in alerts:
        add_exception_helper(user_id, etype, level, details)

    return alerts


def analyze_temperature_critical_from_db(user_id: str, timestamp_str: str):
    """
    Wrapper function: fetches 10 minutes of data from DB and runs the temperature analysis.
    """
    try:
        ts = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("❌ Invalid timestamp format. Use YYYY-MM-DD HH:MM:SS")
        return

    from_ts = (ts - timedelta(minutes=10)).strftime("%Y-%m-%d %H:%M:%S")
    to_ts = timestamp_str

    rows = get_sensor_data_from_date(user_id, from_ts, to_ts)
    if not rows or len(rows) < 300:
        print("ℹ️ Not enough data for 10-minute temperature analysis")
        return

    return analyze_temperature_critical(rows, user_id)
