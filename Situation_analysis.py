import random
from datetime import datetime, timedelta
from model import get_sensor_data

#פונקציית מעטפת לזיהוי עומס חום ומכת חום
def analyze_heat_overload_from_db(user_id: str, timestamp_str: str):
    """
    Loads 5 minutes of data from DB and analyzes for heat overload / heatstroke.
    """
    try:
        ts = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("❌ Invalid timestamp format. Use YYYY-MM-DD HH:MM:SS")
        return

    from_ts = (ts - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    to_ts = timestamp_str

    rows = get_sensor_data(user_id, from_ts, to_ts)
    if not rows or len(rows) < 120:
        print("ℹ️ Not enough data for heat overload analysis (need at least 2–5 minutes)")
        return

    analyze_heat_overload(rows)


#זיהוי עומס חום ומכת חום
def analyze_heat_overload(data_rows):
    """
    Detects early and severe signs of heat overload or heatstroke based on trends over time.
    Assumes 2-second sampling.
    Each row: (timestamp, heart_rate, temperature, movement_level, sweat_level)
    """
    alerts = []

    for i in range(150, len(data_rows)):  # at least 5 min
        ts, hr, temp, move, sweat = data_rows[i]

        win_1min = data_rows[i-29:i+1]
        win_3min = data_rows[i-89:i+1]
        win_5min = data_rows[i-149:i+1]

        # 🔶 Approaching overload: temp 38.1–38.5 & HR 130–150 for >60s
        if all(38.1 <= r[2] <= 38.5 and 130 <= r[1] <= 150 for r in win_1min):
            alerts.append((ts, "heat_overload_warning", "orange", "Temp 38.1–38.5 + HR 130–150 for 60s – early sign of overload"))

        # 🔶 Approaching overload: sweat ≥600 & temp ↑ & HR ↑ over 3–5 min
        temp_start = win_5min[0][2]
        temp_now = temp
        hr_start = win_5min[0][1]
        hr_now = hr
        sweat_avg = sum(r[4] for r in win_5min) / len(win_5min)

        if (
            sweat_avg * 1000 >= 600 and
            temp_start <= 37.8 and temp_now >= 38.3 and
            hr_now - hr_start >= 15
        ):
            alerts.append((ts, "heat_building_up", "orange", "Sweat ≥600 + temp rising + HR↑ ≥15 BPM over 3–5 min"))

        # 🔴 Severe: temp ≥39.0 or (38.5–39.0 + HR ≥150 + no movement)
        if temp >= 39.0:
            alerts.append((ts, "heatstroke", "red", "Temp ≥39.0°C – heatstroke condition"))
        elif 38.5 <= temp < 39.0 and hr >= 150 and all(r[3] <= 0.05 for r in win_1min):
            alerts.append((ts, "heatstroke", "red", "Temp 38.5–39.0 + HR ≥150 + stillness – possible collapse"))

        # 🔴 Severe: HR ≥140 for 60s + temp ≥39.0 + sweat ≥800 + no movement
        if (
            all(r[1] >= 140 for r in win_1min) and
            temp >= 39.0 and
            sweat * 1000 >= 800 and
            all(r[3] == 0 for r in win_1min)
        ):
            alerts.append((ts, "heatstroke_critical", "red", "HR ≥140 + temp ≥39.0 + sweat ≥800 + no movement – critical heatstroke"))

    for ts, etype, level, details in alerts:
        print(f"[{ts}] {level.upper()} – {details}")


from datetime import datetime, timedelta
import random

def generate_fake_data(start_time: datetime, minutes: int = 6, interval_seconds: int = 2):
    """
    Generates synthetic sensor data every X seconds for Y minutes.
    Returns a list of tuples: (timestamp, heart_rate, temperature, movement_level, sweat_level)
    """
    data = []
    current_time = start_time
    total_samples = (minutes * 60) // interval_seconds

    for _ in range(total_samples):
        heart_rate = random.choice([85, 100, 120, 130, 140, 150, 160])
        temperature = round(random.uniform(37.5, 39.2), 1)
        movement_level = random.choice([0.0, 0.03, 0.1, 0.6])
        sweat_level = round(random.uniform(0.4, 0.9), 2)

        data.append((
            current_time.strftime("%Y-%m-%d %H:%M:%S"),
            heart_rate,
            temperature,
            movement_level,
            sweat_level
        ))

        current_time += timedelta(seconds=interval_seconds)

    return data

def main():
    from datetime import datetime
    start = datetime.now()

    # יצירת נתונים פיקטיביים עם עומס חום לצורך בדיקה
    fake_data = generate_fake_data(start, minutes=6, interval_seconds=2)

    # הרצת ניתוח עומס חום
    analyze_heat_overload(fake_data)

if __name__ == "__main__":
    main()
