import sqlite3
import pandas as pd
import os
from .loader import load_data

DB_PATH = "data/transjakarta.db"
CSV_PATH = "data/transjakarta_trips.csv"

def create_db(overwrite=True):
    if overwrite and os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    df = load_data(CSV_PATH)
    # Ensure datetime columns are strings for SQLite
    df["tapInTime"] = df["tapInTime"].astype(str)
    df["tapOutTime"] = df["tapOutTime"].astype(str)
    df.to_sql("trips", conn, if_exists="replace", index=False)
    conn.close()
    print(f"Database created at {DB_PATH} with {len(df)} rows.")

if __name__ == "__main__":
    create_db()