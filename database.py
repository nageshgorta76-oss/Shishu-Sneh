
import sqlite3

# ---------------- CREATE CONNECTION ----------------

conn = sqlite3.connect(
    "database.db",
    check_same_thread=False
)

cursor = conn.cursor()

# ---------------- CREATE TABLE ----------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS baby_data (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    name TEXT,

    age INTEGER,

    weight REAL,

    height REAL

)
""")

conn.commit()

# ---------------- INSERT DATA ----------------

def insert_data(name, age, weight, height):

    cursor.execute("""

    INSERT INTO baby_data(
        name,
        age,
        weight,
        height

    )

    VALUES (?, ?, ?, ?)

    """, (name, age, weight, height))

    conn.commit()

# ---------------- VIEW DATA ----------------

def view_data():

    cursor.execute(
        "SELECT * FROM baby_data ORDER BY name, age, id"
    )

    data = cursor.fetchall()

    return data


def delete_baby_data(name):

    cursor.execute(
        "DELETE FROM baby_data WHERE name = ?",
        (name,)
    )

    conn.commit()

