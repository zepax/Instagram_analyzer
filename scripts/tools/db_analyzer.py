#!/usr/bin/env python3
"""Herramienta para analizar bases de datos SQLite de Instagram"""
import json
import sqlite3
import sys
from pathlib import Path


def analyze_db(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]

        analysis = {"database": str(db_path), "tables": {}}

        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table};")
            count = cursor.fetchone()[0]

            cursor.execute(f"PRAGMA table_info({table});")
            columns = cursor.fetchall()

            analysis["tables"][table] = {
                "row_count": count,
                "columns": [{"name": col[1], "type": col[2]} for col in columns],
            }

        conn.close()
        return analysis
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: db_analyzer.py <database.sqlite>")
        sys.exit(1)

    result = analyze_db(sys.argv[1])
    print(json.dumps(result, indent=2))
