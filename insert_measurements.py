import sqlite3
import pandas as pd

# התחברות לקובץ SQLite
conn = sqlite3.connect("C:/Users/TALYA/Desktop/sqlite/health_monitor.db")

# ת"ז של המשתמש שאת רוצה לשלוף
client_id = "123456789"

# שאילתה שמחזירה את כל המדידות של המשתמש
query = """
SELECT m.*
FROM measurements m
JOIN user_measurements um ON m.id = um.measurement_id
WHERE um.client_id = ?
ORDER BY m.timestamp DESC
"""

# קריאה לתוך DataFrame של pandas
df = pd.read_sql_query(query, conn, params=(client_id,))

print(df)
conn.close()
