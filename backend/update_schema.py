from sqlalchemy import create_engine, text
import time

import os
# Use environment variable or fallback to docker service name 'db'
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@db:5432/hotspot_db")

def update_schema():
    retries = 5
    while retries > 0:
        try:
            engine = create_engine(DATABASE_URL)
            with engine.connect() as conn:
                print("Connected to database.")
                # Add severity column
                try:
                    conn.execute(text("ALTER TABLE reports ADD COLUMN IF NOT EXISTS severity VARCHAR(20) DEFAULT 'Medium'"))
                    conn.execute(text("ALTER TABLE reports ADD COLUMN IF NOT EXISTS road_importance INTEGER DEFAULT 1"))
                    conn.commit()
                    print("Added severity and road_importance columns.")
                except Exception as e:
                    print(f"Column might already exist or error: {e}")
                    
            return
        except Exception as e:
            print(f"Database not ready yet... {e}")
            time.sleep(2)
            retries -= 1

if __name__ == "__main__":
    update_schema()
