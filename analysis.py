import random
from datetime import datetime, timedelta
from model import get_sensor_data

# def generate_fake_data(start_time: datetime, minutes: int = 5, interval_seconds: int = 10):
#     """
#     Generates synthetic sensor data every X seconds for Y minutes.
#     Returns a list of tuples: (timestamp, heart_rate, temperature, movement_level, sweat_level)
#     """
#     data = []
#     current_time = start_time

#     for _ in range((minutes * 60) // interval_seconds):
#         heart_rate = random.choice([72, 80, 95, 102, 110, 130, 160, 180, 42, 48, 38])
#         temperature = round(random.uniform(36.2, 39.0), 1)
#         movement_level = round(random.choice([0.0, 0.05, 0.3, 0.6, 1.0, 1.5, 2.0]), 2)
#         sweat_level = round(random.uniform(0.1, 0.5), 2)

#         data.append((
#             current_time.strftime("%Y-%m-%d %H:%M:%S"),
#             heart_rate,
#             temperature,
#             movement_level,
#             sweat_level
#         ))

#         current_time += timedelta(seconds=interval_seconds)

#     return data

def analyze_heart_rate(data_rows):
    """
    Analyzes a list of health sensor data and prints heart rate anomalies based on medical rules.
    """
    for i, row in enumerate(data_rows):
        ts, hr, temp, move, sweat = row

        # Rule 1: High resting heart rate over 100 BPM
        if hr > 100 and all(r[3] < 0.2 for r in data_rows[max(0, i-3):i+1]):
            print(f"[{ts}] ⚠️ High resting heart rate: {hr} BPM")

        # Rule 2: Critically low heart rate
        if hr < 40:
            print(f"[{ts}] ❗ Critically low heart rate: {hr} BPM")

        # Rule 3: Low heart rate with sudden movement change
        if hr < 50 and i > 0:
            prev_move = data_rows[i-1][3]
            delta_move = abs(move - prev_move)
            if delta_move > 0.8 or (prev_move > 0.5 and move < 0.2):
                print(f"[{ts}] ⚠️ Low heart rate ({hr}) with sudden movement change – possible loss of balance")

        # Rule 4: Heart rate not decreasing after activity
        if i >= 6:
            past_hr = data_rows[i-6][1]  # 1 minute ago (assuming 10-second intervals)
            if past_hr > 100 and hr > past_hr - 12:
                print(f"[{ts}] ⚠️ Heart rate not decreasing post-activity – was {past_hr}, now {hr}")

        # Rule 5: Excessive heart rate during heat and activity
        if temp >= 38.5 and move > 0.5:
            if hr > 150 and move < 1.0:
                print(f"[{ts}] 🚨 Heart rate {hr} too high during mild effort in heat – risk of overheating")
            elif hr > 180:
                print(f"[{ts}] 🚨 Heart rate {hr} dangerously high in full activity and heat – stop and cool down")
  
  
                
                
# def analyze_temperature(data_rows):
#     """
#     Analyzes temperature data and prints alerts based on body heat anomalies.
#     Assumes data_rows: [(timestamp, heart_rate, temperature, movement_level, sweat_level)]
#     """
#     for i, row in enumerate(data_rows):
#         ts, hr, temp, move, sweat = row

#         # Rule: Mild fever (37.6–38.0°C) lasting over 10 minutes
#         if 37.6 <= temp <= 38.0:
#             ten_min_window = data_rows[max(0, i-6):i+1]  # ~1 minute if intervals are 10 sec
#             if all(37.6 <= r[2] <= 38.0 for r in ten_min_window) and len(ten_min_window) >= 6:
#                 print(f"[{ts}] ⚠️ Persistent mild fever (~{temp}°C) for 10+ minutes – monitor closely")

#         # Rule: Moderate fever (38.1–39.0°C)
#         if 38.1 <= temp <= 39.0:
#             if hr > 150:
#                 print(f"[{ts}] 🚨 Moderate fever ({temp}°C) + high heart rate ({hr} BPM) – possible heatstroke!")
#             else:
#                 print(f"[{ts}] ⚠️ Moderate fever ({temp}°C) – possible heat overload or illness")

#         # Rule: High fever (>39.0°C)
#         if temp > 39.0:
#             print(f"[{ts}] ❗ High fever ({temp}°C) – critical condition!")

#         # Rule: Slight drop in temp (36.0–35.5°C) lasting 10+ minutes
#         if 35.5 <= temp <= 36.0:
#             ten_min_window = data_rows[max(0, i-6):i+1]
#             if all(35.5 <= r[2] <= 36.0 for r in ten_min_window) and len(ten_min_window) >= 6:
#                 print(f"[{ts}] ⚠️ Persistent mild cold exposure (~{temp}°C) – possible weather-related drop")

#         # Rule: Mild hypothermia (35.0–35.4°C)
#         if 35.0 <= temp < 35.5:
#             print(f"[{ts}] ⚠️ Mild hypothermia ({temp}°C) – body is starting to lose heat")

#         # Rule: Severe hypothermia (<35.0°C)
#         if temp < 35.0:
#             print(f"[{ts}] ❗ Severe hypothermia ({temp}°C) – immediate danger!")
  
         

            
def analyze_movement(data_rows):
    """
    Analyzes movement data combined with heart rate and temperature to detect critical physical states.
    Assumes data_rows: [(timestamp, heart_rate, temperature, movement_level, sweat_level)]
    """
    for i, row in enumerate(data_rows):
        ts, hr, temp, move, sweat = row

        # Rule 1: Minimal movement for 30+ seconds alone (not enough to alert)
        if i >= 3 and all(r[3] < 0.1 for r in data_rows[i-3:i+1]):
            # only if no other symptoms – no alert
            continue

        # Rule 2: Minimal movement + high heart rate (suspicious)
        if i >= 3 and all(r[3] < 0.1 for r in data_rows[i-3:i+1]) and all(r[1] > 120 for r in data_rows[i-3:i+1]):
            print(f"[{ts}] ⚠️ No movement + high heart rate (>120 BPM) for 30+ seconds – possible collapse or distress")

        # Rule 3: Sudden spike in movement followed by no movement (possible fall)
        if i >= 2:
            prev_move = data_rows[i-2][3]
            peak_move = data_rows[i-1][3]
            now_move = row[3]
            if peak_move - prev_move > 1.0 and now_move < 0.1:
                if hr > 100:
                    print(f"[{ts}] 🚨 Sudden movement spike followed by stillness + HR {hr} – possible fall with no recovery")

        # Rule 4: Fast repeated small movements (tremors)
        if i >= 3:
            last_moves = [r[3] for r in data_rows[i-3:i+1]]
            if all(0.05 <= m <= 0.2 for m in last_moves):
                if hr > 130:
                    print(f"[{ts}] 🚨 Repetitive small movements + high HR ({hr}) – possible seizure or panic attack")
                else:
                    print(f"[{ts}] 😰 Repetitive small movements – possible tremor, keep monitoring")

        # Rule 5: No movement + abnormal temp + extreme HR → emergency
        if move < 0.1 and (temp > 39.0 or temp < 35.0) and (hr > 140 or hr < 40):
            print(f"[{ts}] 🟥 No movement + abnormal temperature ({temp}°C) + critical HR ({hr}) – possible unconsciousness!")



#פונקציית מעטפת לניתוח אירועי זיעה
def analyze_sweat_critical_events(data_rows):
    """
    Analyzes sweat level anomalies using time-based conditions.
    Each row: (timestamp, heart_rate, temperature, movement_level, sweat_level)
    Assumes sampling every 2 seconds.
    """
    alerts = []

    for i in range(30, len(data_rows)):
        ts, hr, temp, move, sweat = data_rows[i]

        # 15 samples = 30 seconds, 10 = 20s, 8 = 16s, 5 = 10s, 60 = 2 minutes
        win_30s = data_rows[i-14:i+1]
        win_20s = data_rows[i-9:i+1]
        win_15s = data_rows[i-7:i+1]
        win_10s = data_rows[i-4:i+1]
        win_2min = data_rows[i-59:i+1]

        # Scenario 1: Heat overload (high sweat + high temp + high HR for 30s)
        if all(r[4]*1000 > 600 and r[2] > 38.0 and r[1] > 150 for r in win_30s):
            alerts.append((ts, "heatstroke", "red", "Persistent sweat >600 + HR>150 + temp>38°C – heat overload"))

        # Scenario 2: High sweat + HR drop or high at rest (20s)
        if all(r[4]*1000 > 800 for r in win_20s):
            hr_drop = win_20s[0][1] - hr
            if hr_drop > 20 or (hr > 120 and move < 0.2):
                level = "red" if all(r[3] < 0.2 for r in win_20s) else "orange"
                alerts.append((ts, "dehydration", level, "High sweat >800 + HR abnormal → possible collapse"))

        # Scenario 3: Sudden sweat spike while still, lasting >15s
        deltas = [abs(data_rows[j][4] - data_rows[j-1][4]) for j in range(i-7, i+1)]
        if all(d > 0.25 for d in deltas) and all(data_rows[j][3] < 0.1 for j in range(i-7, i+1)):
            if all(data_rows[j][1] > 130 or data_rows[j][2] > 37.5 for j in range(i-7, i+1)):
                alerts.append((ts, "anxiety_attack", "orange", "Sharp sweat fluctuation while still – possible nervous reaction"))

        # Scenario 4: Sudden sweat at rest + extreme HR
        if move < 0.05 and (hr < 50 or hr > 160) and sweat > 0.6:
            if all(data_rows[j][4] > 0.6 for j in range(i-4, i+1)):
                alerts.append((ts, "collapse", "red", "Sweat surge + abnormal HR at rest – critical state"))

        # Scenario 5: Persistent high sweat over 2 minutes
        if all(r[4] > 0.7 for r in win_2min):
            if all(60 <= r[1] <= 110 and 0.2 <= r[3] <= 1.5 for r in win_2min):
                alerts.append((ts, "fatigue_or_sensor", "orange", "Sweat remains high >2 minutes despite normalized vitals"))

        # Scenario 6: Sudden sweat while all vitals calm
        if i > 1:
            calm = all(r[3] < 0.1 and 60 <= r[1] <= 100 and 36.5 <= r[2] <= 37.5 for r in data_rows[i-2:i+1])
            spike = sweat - data_rows[i-1][4] > 0.4
            if calm and spike:
                alerts.append((ts, "possible_sensor_fault", "uncertain", "Sudden sweat surge while calm – possible water spill or sensor issue"))

    for ts, etype, level, details in alerts:
        print(f"[{ts}] {level.upper()} – {details}")


from datetime import datetime, timedelta
from model import get_sensor_data

def analyze_sweat_critical_events_from_db(user_id: str, timestamp_str: str):
    """
    Loads 2 minutes of data from DB and analyzes sweat-related time-based anomalies.
    """
    try:
        ts = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("❌ Invalid timestamp format. Use YYYY-MM-DD HH:MM:SS")
        return

    from_ts = (ts - timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")
    to_ts = timestamp_str

    rows = get_sensor_data(user_id, from_ts, to_ts)

    if not rows or len(rows) < 60:
        print("ℹ️ Not enough data for sweat trend analysis (need ~60 samples)")
        return

    analyze_sweat_critical_events(rows)



#פונקציית מעטפת לחרדה
def analyze_anxiety_attack_from_db(user_id: str, timestamp_str: str):
    """
    Loads 60 seconds of data before the given timestamp for the specified user
    and runs anxiety attack analysis.
    """
    try:
        ts = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("❌ Invalid timestamp format. Use YYYY-MM-DD HH:MM:SS")
        return

    # Load 60 seconds of data before the timestamp
    from_ts = (ts - timedelta(seconds=60)).strftime("%Y-%m-%d %H:%M:%S")
    to_ts = timestamp_str

    data_rows = get_sensor_data(user_id, from_ts, to_ts)

    if not data_rows or len(data_rows) < 30:
        print("ℹ️ Not enough data to analyze for anxiety attack (need ~30+ records)")
        return

    analyze_anxiety_attack(data_rows)


#התקף חרדה
def analyze_anxiety_attack(data_rows): 
    """
    Analyzes sequences of sensor data to detect anxiety attack scenarios.
    Assumes sampling every 2 seconds.
    Each row: (timestamp, heart_rate, temperature, movement_level, sweat_level)
    """
    for i in range(30, len(data_rows)):  # start after 60 seconds of data
        ts, hr, temp, move, sweat = data_rows[i]

        # Extract time windows based on 2-second intervals
        window_30s = data_rows[i-14:i+1]   # last 30 seconds (~15 samples)
        window_45s = data_rows[i-22:i+1]   # last 45 seconds (~23 samples)
        window_60s = data_rows[i-29:i+1]   # last 60 seconds (~30 samples)

        # Scenario 1: Classic panic attack
        if (
            window_30s[0][1] < 95 and hr >= 120 and
            window_30s[0][4]*1000 < 500 and sweat*1000 >= 900 and
            window_30s[0][2] < 36.9 and temp >= 37.4 and
            all(0.05 <= r[3] <= 0.2 for r in window_30s)
        ):
            print(f"[{ts}] 🟥 Classic panic attack detected – sudden rise in HR, sweat, temp and shaking")

        # Scenario 2: Silent anxiety (little movement)
        if (
            window_45s[0][1] < 90 and hr >= 135 and
            all(0.05 <= r[3] <= 0.4 for r in window_45s) and
            sweat - window_45s[0][4] > 0.4 and
            temp < 37.3
        ):
            print(f"[{ts}] 🟧 Possible silent anxiety attack – HR and sweat rising despite little movement")

        # Scenario 3: Nerve tremor with stable vitals
        if (
            all(0.05 <= r[3] <= 0.2 for r in window_30s) and
            window_30s[0][4]*1000 < 500 and sweat*1000 >= 700 and
            95 <= hr <= 115 and
            all(abs(r[2] - temp) < 0.2 for r in window_30s)
        ):
            print(f"[{ts}] 🟨 Mild tremor detected – stable HR and temp, continue monitoring")

        # Scenario 4: Panic with possible collapse
        if (
            window_60s[0][1] <= 100 and hr >= 150 and
            sweat >= 0.8 and
            data_rows[i-2][3] > 1.0 and move < 0.1 and
            temp > window_60s[0][2]
        ):
            print(f"[{ts}] 🟥 Severe anxiety with collapse risk – sudden stop after strong movement, HR {hr}")



#פונקציית מעטפת לניתוח התייבשות
def analyze_dehydration_from_db(user_id: str, timestamp_str: str):
    """
    Loads 5 minutes of sensor data from the database for the given user and timestamp,
    and runs dehydration analysis.
    """
    try:
        ts = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("❌ Invalid timestamp format. Use YYYY-MM-DD HH:MM:SS")
        return

    from_ts = (ts - timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S")
    to_ts = timestamp_str

    data_rows = get_sensor_data(user_id, from_ts, to_ts)

    if not data_rows or len(data_rows) < 60:
        print("ℹ️ Not enough data for dehydration analysis (need at least 60 records)")
        return

    analyze_dehydration(data_rows)


#זיהוי התייבשות
def analyze_dehydration(data_rows):
    """
    Detects dehydration scenarios based on trends in heart rate, sweat, temperature, and movement over time.
    Assumes 2-second sampling interval.
    Each row: (timestamp, heart_rate, temperature, movement_level, sweat_level)
    """
    for i in range(60, len(data_rows)):
        ts, hr, temp, move, sweat = data_rows[i]

        # Windows for trend analysis
        win_1min = data_rows[i-29:i+1]     # 1 minute (~30 samples)
        win_3min = data_rows[i-89:i+1]     # 3 minutes
        win_4min = data_rows[i-119:i+1]    # 4 minutes
        win_5min = data_rows[i-149:i+1]    # 5 minutes

        # Scenario 1: Moderate dehydration developing
        if len(win_5min) == 150:
            hr_start = win_5min[0][1]
            hr_now = hr
            hr_delta = hr_now - hr_start
            sweat_start = win_5min[0][4] * 1000
            sweat_now = sweat * 1000
            avg_temp = sum(r[2] for r in win_5min) / len(win_5min)
            move_trend = win_5min[0][3] - move

            if 8 <= hr_delta <= 12 and sweat_now <= 300 and sweat_start >= 600 and 37.8 <= avg_temp <= 38.0 and move_trend > 0.2:
                print(f"[{ts}] 🟧 Developing moderate dehydration – rising HR, sweat drop, stable temp, reduced movement")

        # Scenario 2: Severe dehydration
        if len(win_4min) == 120:
            hr_start = win_4min[0][1]
            if hr_start >= 90 and hr >= 130:
                sweat_min = min(r[4]*1000 for r in win_4min)
                temp_start = win_4min[0][2]
                if sweat_min < 200 and temp - temp_start >= 0.8 and all(r[3] < 0.2 for r in win_1min):
                    print(f"[{ts}] 🟥 Severe dehydration – HR↑, sweat≈0, temp↑, no movement – stop immediately")

        # Scenario 3: Early dehydration suspicion
        if len(win_5min) == 150:
            hr_start = win_5min[0][1]
            if hr_start <= 72 and 85 >= hr >= 80:
                sweat_start = win_5min[0][4]*1000
                if sweat_start >= 500 and sweat*1000 <= 350:
                    avg_temp = sum(r[2] for r in win_5min) / len(win_5min)
                    if 37.1 <= avg_temp <= 37.5 and all(0.3 <= r[3] <= 1.5 for r in win_5min):
                        print(f"[{ts}] 🟨 Early signs of dehydration – monitoring only")

        # Scenario 4: Dehydration collapse
        if (
            i >= 2 and
            data_rows[i-2][1] >= 100 and hr < 60 and
            sweat == 0.0 and
            temp >= 38.0 and
            move < 0.05
        ):
            print(f"[{ts}] 🟥 COLLAPSE from dehydration – sharp HR drop + no sweat/movement + high temp – LIFE THREAT")



#פונקציית מעטפת לניתוח התעלפות
def analyze_collapse_events_from_db(user_id: str, timestamp_str: str):
    """
    Loads 60 seconds of sensor data from the database for the given user and timestamp,
    and runs collapse detection analysis.
    """
    try:
        ts = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("❌ Invalid timestamp format. Use YYYY-MM-DD HH:MM:SS")
        return

    from_ts = (ts - timedelta(seconds=60)).strftime("%Y-%m-%d %H:%M:%S")
    to_ts = timestamp_str

    data_rows = get_sensor_data(user_id, from_ts, to_ts)

    if not data_rows or len(data_rows) < 60:
        print("ℹ️ Not enough data for collapse analysis (need at least 60 records)")
        return

    analyze_collapse_events(data_rows)




#התעלפות
def analyze_collapse_events(data_rows):
    """
    Detects critical collapse scenarios from combined sensor data.
    Assumes 2-second sampling.
    Each row: (timestamp, heart_rate, temperature, movement_level, sweat_level)
    """
    for i in range(60, len(data_rows)):
        ts, hr, temp, move, sweat = data_rows[i]

        window_30s = data_rows[i-14:i+1]
        window_60s = data_rows[i-29:i+1]

        # Scenario 1: Collapse after physical overload
        if (
            data_rows[i-15][3] > 1.0 and all(r[3] < 0.1 for r in window_30s) and
            120 <= data_rows[i-15][1] <= 150 and 50 <= hr <= 60 and
            temp >= 38.0 and
            data_rows[i-15][4] >= 0.8 and sweat < 0.2
        ):
            print(f"[{ts}] 🟥 COLLAPSE after physical overload – movement stopped, HR dropped, temp high, sweat vanished")

        # Scenario 2: Heatstroke + unconsciousness
        if (
            all(r[3] < 0.1 for r in window_60s) and
            all(r[1] > 140 for r in window_60s) and
            temp > 39.0 and
            sweat >= 0.9
        ):
            print(f"[{ts}] 🟥 Possible HEATSTROKE + unconsciousness – persistent high HR, sweat, temp, no movement")

        # Scenario 3: Collapse from dehydration or hypothermia
        if (
            move < 0.05 and
            data_rows[i-2][1] >= 80 and hr < 50 and
            temp < 35.5 and
            sweat < 0.1
        ):
            print(f"[{ts}] 🟥 COLLAPSE from dehydration/hypothermia – zero movement, low temp, HR crash, dry skin")


#חום והיפוטרמיה
def analyze_temperature_critical(data_rows):
    """
    Detects heat-related and hypothermia-related temperature anomalies over time.
    Assumes 2-second sampling. Each row: (timestamp, heart_rate, temperature, movement_level, sweat_level)
    """
    alerts = []

    for i in range(300, len(data_rows)):  # 10 minutes = 300 samples
        ts, hr, temp, move, sweat = data_rows[i]

        window_10min = data_rows[i-299:i+1]

        # Mild fever (37.6–38.0°C) for >10 minutes
        if all(37.6 <= r[2] <= 38.0 for r in window_10min):
            alerts.append((ts, "mild_fever", "orange", "Mild fever (37.6–38.0°C) lasting over 10 minutes – possible early illness or exertion"))

        # Moderate fever (38.1–39.0°C)
        if 38.1 <= temp <= 39.0:
            if hr > 150:
                alerts.append((ts, "heatstroke_risk", "red", f"Temp {temp}°C + HR {hr} – CRITICAL heat overload"))
            else:
                alerts.append((ts, "moderate_fever", "orange", f"Moderate fever ({temp}°C) – possible heat overload or illness"))

        # High fever >39.0°C
        if temp > 39.0:
            alerts.append((ts, "heatstroke", "red", f"High fever {temp}°C – IMMEDIATE heatstroke danger"))

        # Mild cooling (36.0–35.5°C) >10 minutes
        if all(35.5 <= r[2] <= 36.0 for r in window_10min):
            alerts.append((ts, "mild_cooling", "orange", "Body temp low (35.5–36.0°C) for over 10 minutes – possible cold stress or fatigue"))

        # Mild hypothermia (35.0–35.4°C)
        if 35.0 <= temp < 35.5:
            alerts.append((ts, "mild_hypothermia", "red", f"Mild hypothermia ({temp}°C) – monitor for deterioration"))

        # Severe hypothermia (<35.0°C)
        if temp < 35.0:
            alerts.append((ts, "severe_hypothermia", "red", f"Severe hypothermia ({temp}°C) – MEDICAL EMERGENCY"))

    for ts, etype, level, details in alerts:
        print(f"[{ts}] {level.upper()} – {details}")

  
  



def generate_fake_sensor_data(
    start_time: datetime,
    minutes: int = 5,
    interval_seconds: int = 2,
    hr_range=(70, 110),
    temp_range=(36.5, 37.8),
    move_range=(0.0, 1.5),
    sweat_range=(0.1, 0.6)
):
    """
    Generates fake sensor data with given ranges.
    
    Parameters:
        - start_time (datetime): when the data starts
        - minutes (int): duration of data in minutes
        - interval_seconds (int): interval between each sample
        - hr_range (tuple): heart rate range (BPM)
        - temp_range (tuple): temperature range (°C)
        - move_range (tuple): movement level range
        - sweat_range (tuple): sweat level range (0–1)
    
    Returns:
        List of tuples: (timestamp, heart_rate, temperature, movement_level, sweat_level)
    """
    data = []
    current_time = start_time
    total_samples = (minutes * 60) // interval_seconds

    for _ in range(total_samples):
        heart_rate = random.randint(*hr_range)
        temperature = round(random.uniform(*temp_range), 1)
        movement_level = round(random.uniform(*move_range), 2)
        sweat_level = round(random.uniform(*sweat_range), 2)

        data.append((
            current_time.strftime("%Y-%m-%d %H:%M:%S"),
            heart_rate,
            temperature,
            movement_level,
            sweat_level
        ))
        current_time += timedelta(seconds=interval_seconds)

    return data


# def main():
#     start = datetime.now()
#     fake_data = generate_fake_data(start)
#     analyze_heart_rate(fake_data)
#     analyze_temperature(fake_data)
#     analyze_movement(fake_data)
#     analyze_sweat_level(fake_data)
#     analyze_anxiety_attack(fake_data)
#     print("Analysis complete.")
# if __name__ == "__main__":
#     main()


def main():
    # יצירת נתונים פיקטיביים של עומס חום: טמפ׳ גבוהה, דופק גבוה, תנועה נמוכה
    fake_data = generate_fake_sensor_data(
        start_time=datetime.now(),
        minutes=6,
        interval_seconds=2,
        hr_range=(135, 160),           # דופק גבוה
        temp_range=(38.4, 39.2),       # טמפ׳ גבוהה מאוד
        move_range=(0.0, 0.1),         # כמעט בלי תזוזה
        sweat_range=(0.7, 0.95)        # רטיבות גבוהה
    )

    # הרצת ניתוח עומס חום
    analyze_temperature_critical(fake_data)

if __name__ == "__main__":
    main()