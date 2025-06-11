import sqlite3
from datetime import datetime, timedelta

def detect_heat_stroke_risk(db_path, measurement_id, timestamp_str):
    """
    Detects early or immediate signs of heat stroke based on recent health measurements.

    Parameters:
    db_path (str): Path to the SQLite database file.
    measurement_id (int): ID of the measurement from the 'user_measurements' table.
    timestamp_str (str): Timestamp of the measurement in format 'YYYY-MM-DD HH:MM:SS'.

    The function identifies the client_id for the given measurement_id,
    fetches the user's measurements from the last 5 minutes,
    and triggers an alert with the appropriate severity.
    """

    def send_alert(message, client_id):
        # Placeholder for actual alert logic (e.g., send push + SMS)
        print(f"ALERT: {message} | User: {client_id}")

    try:
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("Invalid timestamp format. Use 'YYYY-MM-DD HH:MM:SS'")
        return

    time_limit = timestamp - timedelta(minutes=5)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT client_id FROM user_measurements
        WHERE measurement_id = ?
    """, (measurement_id,))
    result = cursor.fetchone()

    if not result:
        print("measurement_id not found in user_measurements table.")
        conn.close()
        return

    client_id = result[0]

    cursor.execute("""
        SELECT m.heart_rate, m.body_temp, m.sweat_level
        FROM user_measurements um
        JOIN measurements m ON um.measurement_id = m.id
        WHERE um.client_id = ?
        AND m.timestamp BETWEEN ? AND ?
        ORDER BY m.timestamp ASC
    """, (client_id, time_limit.strftime("%Y-%m-%d %H:%M:%S"), timestamp_str))

    rows = cursor.fetchall()
    conn.close()

    if len(rows) < 2:
        return  # Not enough data to evaluate trends

    heart_rates = [r[0] for r in rows]
    temps = [r[1] for r in rows]
    sweats = [r[2] for r in rows]

    risk_score = 0

    # Critical signs
    if any(temp >= 39.0 for temp in temps):
        risk_score += 2

    if sum(1 for hr in heart_rates if hr >= 130) >= 2:
        risk_score += 1.5

    if min(sweats) < 20 and any(temp >= 39.0 for temp in temps):
        risk_score += 2

    # Early warning signs
    if any(37.5 <= temp < 39.0 for temp in temps):
        risk_score += 1

    if any(110 <= hr < 130 for hr in heart_rates):
        risk_score += 1

    if max(sweats) > 30 and sweats[-1] < 20:
        risk_score += 1

    # Decision based on score
    if risk_score >= 4:
        send_alert("Severe heat stroke risk", client_id)
    elif risk_score >= 2:
        send_alert("Early heat stroke warning", client_id)













def detect_immediate_dehydration_risk_precise(db_path, measurement_id, timestamp_str):
    """
    Detects signs of dehydration risk for a specific user based on recent health measurements.
    Sends an early warning or a severe alert based on weighted condition scoring.

    Parameters:
    db_path (str): Path to the SQLite database file.
    measurement_id (int): ID of the measurement from the 'user_measurements' table.
    timestamp_str (str): Timestamp of the measurement in format 'YYYY-MM-DD HH:MM:SS'.
    """

    def send_alert(problem_name, client_id):
        # Placeholder function for sending alerts (can be replaced with real implementation).
        print(f"ALERT: {problem_name} | User: {client_id}")

    try:
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("Invalid timestamp format. Use 'YYYY-MM-DD HH:MM:SS'")
        return

    time_limit = timestamp - timedelta(minutes=5)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT client_id FROM user_measurements
        WHERE measurement_id = ?
    """, (measurement_id,))
    result = cursor.fetchone()

    if not result:
        print("measurement_id not found in user_measurements table.")
        conn.close()
        return

    client_id = result[0]

    cursor.execute("""
        SELECT m.heart_rate, m.body_temp, m.oxygen_level, m.sweat_level
        FROM user_measurements um
        JOIN measurements m ON um.measurement_id = m.id
        WHERE um.client_id = ?
        AND m.timestamp BETWEEN ? AND ?
        ORDER BY m.timestamp ASC
    """, (client_id, time_limit.strftime("%Y-%m-%d %H:%M:%S"), timestamp_str))

    rows = cursor.fetchall()
    conn.close()

    if len(rows) < 2:
        return  # Not enough data to evaluate trends

    heart_rates = [r[0] for r in rows]
    temps = [r[1] for r in rows]
    oxygens = [r[2] for r in rows]
    sweats = [r[3] for r in rows]

    risk_score = 0

    # Condition 1: Heart rate increased by more than 10 BPM (low-medium weight)
    if heart_rates[-1] - heart_rates[0] > 10:
        risk_score += 1

    # Condition 2: Temperature increased from ≤36.7 to >37.5 (medium-high weight)
    if temps[0] <= 36.7 and max(temps) > 37.5:
        risk_score += 1.5

    # Condition 3: Sweat level dropped below 20 and kept dropping (high weight)
    if min(sweats) < 20 and sweats[-1] < sweats[0]:
        risk_score += 2

    # Condition 4: Oxygen level dropped from >97 to <95 (low weight)
    if oxygens[0] > 97 and min(oxygens) < 95:
        risk_score += 1

    # Trigger alerts based on severity
    if risk_score >= 4:
        send_alert("Severe dehydration risk", client_id)
    elif risk_score >= 2:
        send_alert("Early dehydration warning", client_id)




def detect_hypothermia_risk(db_path, measurement_id, timestamp_str):
    """
    Detects early or severe signs of hypothermia based on recent health measurements.

    Parameters:
    db_path (str): Path to the SQLite database file.
    measurement_id (int): ID of the measurement from the 'user_measurements' table.
    timestamp_str (str): Timestamp of the measurement in format 'YYYY-MM-DD HH:MM:SS'.

    The function identifies the client_id for the given measurement_id,
    fetches the user's measurements from the last 5 minutes,
    and triggers an alert based on physiological signs of hypothermia.
    """

    def send_alert(message, client_id):
        # Placeholder for actual alert logic (e.g., send push + SMS)
        print(f"ALERT: {message} | User: {client_id}")

    try:
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        print("Invalid timestamp format. Use 'YYYY-MM-DD HH:MM:SS'")
        return

    time_limit = timestamp - timedelta(minutes=5)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT client_id FROM user_measurements
        WHERE measurement_id = ?
    """, (measurement_id,))
    result = cursor.fetchone()

    if not result:
        print("measurement_id not found in user_measurements table.")
        conn.close()
        return

    client_id = result[0]

    cursor.execute("""
        SELECT m.body_temp, m.motion_level, m.sweat_level
        FROM user_measurements um
        JOIN measurements m ON um.measurement_id = m.id
        WHERE um.client_id = ?
        AND m.timestamp BETWEEN ? AND ?
        ORDER BY m.timestamp ASC
    """, (client_id, time_limit.strftime("%Y-%m-%d %H:%M:%S"), timestamp_str))

    rows = cursor.fetchall()
    conn.close()

    if len(rows) < 2:
        return  # Not enough data to evaluate trends

    temps = [r[0] for r in rows]
    motions = [r[1] for r in rows]   # Assume this is a numeric representation of tremors or acceleration
    sweats = [r[2] for r in rows]

    risk_score = 0

    # Critical: temperature dropped below 35°C
    if any(temp < 35.0 for temp in temps):
        risk_score += 2

    # Sustained motion indicating repeated shivering
    tremor_count = sum(1 for m in motions if m > 1.5)  # You may adjust threshold based on sensor scale
    if tremor_count >= 2:
        risk_score += 1.5

    # Low sweat level (optional support condition)
    if max(sweats) < 20:
        risk_score += 1

    # Trigger alerts based on total score
    if risk_score >= 4:
        send_alert("Severe hypothermia risk", client_id)
    elif risk_score >= 2:
        send_alert("Early hypothermia warning", client_id)




