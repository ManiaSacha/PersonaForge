import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from backend.users.models import Base

DATABASE_URL = "sqlite+aiosqlite:///./personaforge.db"

async def init_db():
    print("Creating database tables...")
    
    engine = create_async_engine(DATABASE_URL)
    
    async with engine.begin() as conn:
        # Drop all tables if they exist
        await conn.run_sync(Base.metadata.drop_all)
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(init_db())
