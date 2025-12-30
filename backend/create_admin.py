from sqlalchemy import create_engine, text
from passlib.context import CryptContext

import os
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5433/hotspot_db")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_admin():
    engine = create_engine(DATABASE_URL)
    with engine.connect() as conn:
        # Check if admin exists
        exists = conn.execute(text("SELECT 1 FROM users WHERE email='admin@example.com'")).scalar()
        if not exists:
            pw_hash = pwd_context.hash("admin123")
            conn.execute(text(f"INSERT INTO users (name, email, password_hash, role) VALUES ('Admin User', 'admin@example.com', '{pw_hash}', 'admin')"))
            conn.commit()
            print("Admin user created.")
        else:
            print("Admin user already exists.")

if __name__ == "__main__":
    create_admin()
