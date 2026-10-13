import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "garden.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS harvests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                crop TEXT NOT NULL,
                harvest_date TEXT NOT NULL,
                quantity REAL NOT NULL CHECK(quantity > 0),
                unit TEXT NOT NULL,
                price_per_unit REAL NOT NULL CHECK(price_per_unit >= 0),
                cost REAL NOT NULL CHECK(cost >= 0),
                revenue REAL NOT NULL CHECK(revenue >= 0),
                note TEXT NOT NULL DEFAULT ''
            )
            """
        )


def add_harvest(crop, harvest_date, quantity, unit, price_per_unit, cost, revenue, note=""):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO harvests
            (crop, harvest_date, quantity, unit, price_per_unit, cost, revenue, note)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (crop, harvest_date, quantity, unit, price_per_unit, cost, revenue, note),
        )


def get_harvests():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, crop, harvest_date, quantity, unit,
                   price_per_unit, cost, revenue, note
            FROM harvests
            ORDER BY harvest_date DESC, id DESC
            """
        ).fetchall()
    return [dict(row) for row in rows]


def delete_harvest(harvest_id):
    with get_connection() as connection:
        connection.execute("DELETE FROM harvests WHERE id = ?", (harvest_id,))
