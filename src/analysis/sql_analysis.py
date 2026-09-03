import sqlite3
import pandas as pd
import os

DB_PATH = "data/transjakarta.db"
SQL_FILE = "sql/analysis.sql"

def run_queries():
    if not os.path.exists(DB_PATH):
        print("Database not found. Run src/data/database.py first.")
        return
    conn = sqlite3.connect(DB_PATH)
    with open(SQL_FILE, "r") as f:
        sql = f.read()
    # Split by semicolon (simple)
    queries = [q.strip() for q in sql.split(";") if q.strip()]
    for i, query in enumerate(queries, 1):
        print(f"\n--- Query {i} ---")
        try:
            df = pd.read_sql_query(query, conn)
            print(df.to_string(index=False))
        except Exception as e:
            print(f"Error: {e}")
    conn.close()

if __name__ == "__main__":
    run_queries()