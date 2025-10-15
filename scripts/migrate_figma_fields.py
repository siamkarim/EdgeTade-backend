"""
Migration script to add new fields from Figma designs
"""
import asyncio
import sys
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from loguru import logger

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings

async def run_migration():
    """Add new fields from Figma designs"""
    logger.info("Starting migration for Figma design fields...")
    
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with AsyncSessionLocal() as session:
        try:
            # Add new profile fields
            await session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS id_number VARCHAR(50);
            """))
            
            await session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS date_of_birth TIMESTAMP WITH TIME ZONE;
            """))
            
            # Add email verification code fields
            await session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS email_verification_code VARCHAR(6);
            """))
            
            await session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS email_verification_code_expires TIMESTAMP WITH TIME ZONE;
            """))
            
            # Add password reset fields
            await session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS password_reset_token VARCHAR(255);
            """))
            
            await session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS password_reset_expires TIMESTAMP WITH TIME ZONE;
            """))
            
            await session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS password_reset_code VARCHAR(6);
            """))
            
            await session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS password_reset_code_expires TIMESTAMP WITH TIME ZONE;
            """))
            
            await session.commit()
            logger.info("✅ Successfully added Figma design fields to users table.")
            
        except Exception as e:
            await session.rollback()
            logger.error(f"❌ Migration failed: {e}")
            raise

    await engine.dispose()
    logger.info("Migration completed.")

if __name__ == "__main__":
    asyncio.run(run_migration())
