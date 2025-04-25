# scripts/init_db.py

from utils.database import reset_db

if __name__ == "__main__":
    reset_db()
    print("✅ Database initialization complete.")
