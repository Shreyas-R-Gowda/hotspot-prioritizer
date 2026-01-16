import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://admin:admin123@localhost:5432/citizen_ai")

async def init_db():
    """Initialize database with required extensions and tables."""
    engine = create_async_engine(DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        # Enable PostGIS extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis;"))
        
        # Enable pgvector extension
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        
        print("✅ Database extensions initialized successfully!")
        print("   - PostGIS: Enabled")
        print("   - pgvector: Enabled")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
