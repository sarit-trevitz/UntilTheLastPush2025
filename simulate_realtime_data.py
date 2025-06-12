from model import add_user, add_sensor_data
from datetime import datetime, timedelta

# הגדר משתמשים
users = {
    "111111111": {"first_name": "Anxious", "last_name": "Soldier"},
    "222222222": {"first_name": "Calm", "last_name": "Soldier"},
    "333333333": {"first_name": "Stable", "last_name": "Soldier"},
}

# יוצרים משתמשים במסד
for user_id, info in users.items():
    add_user(user_id, info["first_name"], info["last_name"])

# זמן התחלה בסיסי
start_time = datetime.now() - timedelta(seconds=20)

# 10 מדידות לכל חייל
for i in range(10):
    ts = (start_time + timedelta(seconds=i*2)).strftime("%Y-%m-%d %H:%M:%S")

    # חייל 1 – סימנים של התקף חרדה מתגברים בהדרגה
    add_sensor_data("111111111", {
        "heart_rate": 85 + i*3,
        "temperature": 36.5 + (i * 0.05),
        "movement_level": 0.3 - (i * 0.01),
        "sweat_level": 0.6 - (i * 0.05),
        "timestamp": ts
    })

    # חייל 2 – מדדים רגועים
    add_sensor_data("222222222", {
        "heart_rate": 75,
        "temperature": 36.5,
        "movement_level": 0.5,
        "sweat_level": 0.5,
        "timestamp": ts
    })

    # חייל 3 – תזוזות ורעש אבל לא חרדה
    add_sensor_data("333333333", {
        "heart_rate": 90 + (i % 2),
        "temperature": 36.7,
        "movement_level": 0.4 + (0.1 if i % 3 == 0 else 0),
        "sweat_level": 0.45,
        "timestamp": ts
    })
