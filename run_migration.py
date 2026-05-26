#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Execute database migration script"""
import sys
from pathlib import Path
from sqlalchemy import create_engine, text

# Database connection URL (using psycopg driver)
DATABASE_URL = "postgresql+psycopg://huanxing:huanxing@localhost:15432/huanxing"

def run_migration(sql_file: str):
    """Execute migration SQL file"""
    sql_path = Path(sql_file)
    if not sql_path.exists():
        print(f"Error: SQL file not found: {sql_file}")
        return False

    print(f"Reading migration file: {sql_file}")
    sql_content = sql_path.read_text(encoding='utf-8')

    try:
        print(f"Connecting to database...")
        engine = create_engine(DATABASE_URL)

        with engine.connect() as conn:
            print("Executing migration...")
            conn.execute(text(sql_content))
            conn.commit()
            print("Migration executed successfully!")

        return True

    except Exception as e:
        print(f"Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python run_migration.py <sql_file>")
        sys.exit(1)

    sql_file = sys.argv[1]
    success = run_migration(sql_file)
    sys.exit(0 if success else 1)
