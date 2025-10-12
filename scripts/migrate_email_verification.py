#!/usr/bin/env python3
"""
Database migration script to add email verification columns
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine
from sqlalchemy import text
from loguru import logger


async def add_email_verification_columns():
    """Add email verification columns to users table"""
    logger.info("Adding email verification columns to users table...")
    
    try:
        async with engine.begin() as conn:
            # Add email verification columns
            await conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS email_verification_token VARCHAR(255),
                ADD COLUMN IF NOT EXISTS email_verification_expires TIMESTAMP WITH TIME ZONE
            """))
            
            logger.info("✅ Email verification columns added successfully")
            
    except Exception as e:
        logger.error(f"❌ Failed to add email verification columns: {e}")
        raise


async def main():
    """Main migration function"""
    logger.info("=" * 60)
    logger.info("EdgeTrade Database Migration - Email Verification")
    logger.info("=" * 60)
    
    try:
        await add_email_verification_columns()
        logger.info("")
        logger.info("=" * 60)
        logger.info("✅ Migration completed successfully!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return


if __name__ == "__main__":
    asyncio.run(main())
