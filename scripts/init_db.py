# scripts/init_db.py

from api.db_utils import init_db

if __name__ == "__main__":
    init_db()
    print("✅ Database initialization complete.")
