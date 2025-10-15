"""
Database migration script to change full_name to first_name and last_name
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import engine
from sqlalchemy import text
from loguru import logger


async def migrate_name_fields():
    """Migrate full_name field to first_name and last_name"""
    logger.info("Starting migration: full_name -> first_name, last_name")
    
    try:
        async with engine.begin() as conn:
            # Check if first_name column already exists
            result = await conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'first_name'
            """))
            
            if result.fetchone():
                logger.info("Migration already completed - first_name column exists")
                return
            
            # Add new columns
            logger.info("Adding first_name and last_name columns...")
            await conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN first_name VARCHAR(100),
                ADD COLUMN last_name VARCHAR(100)
            """))
            
            # Migrate existing data
            logger.info("Migrating existing full_name data...")
            await conn.execute(text("""
                UPDATE users 
                SET first_name = CASE 
                    WHEN full_name IS NOT NULL AND position(' ' in full_name) > 0 
                    THEN split_part(full_name, ' ', 1)
                    ELSE full_name
                END,
                last_name = CASE 
                    WHEN full_name IS NOT NULL AND position(' ' in full_name) > 0 
                    THEN substring(full_name from position(' ' in full_name) + 1)
                    ELSE NULL
                END
                WHERE full_name IS NOT NULL
            """))
            
            # Drop the old column
            logger.info("Dropping full_name column...")
            await conn.execute(text("ALTER TABLE users DROP COLUMN full_name"))
            
            logger.info("✅ Migration completed successfully!")
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise


async def rollback_migration():
    """Rollback migration - restore full_name column"""
    logger.info("Rolling back migration...")
    
    try:
        async with engine.begin() as conn:
            # Add full_name column back
            await conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN full_name VARCHAR(255)
            """))
            
            # Restore data
            await conn.execute(text("""
                UPDATE users 
                SET full_name = CASE 
                    WHEN last_name IS NOT NULL 
                    THEN CONCAT(first_name, ' ', last_name)
                    ELSE first_name
                END
            """))
            
            # Drop new columns
            await conn.execute(text("""
                ALTER TABLE users 
                DROP COLUMN first_name,
                DROP COLUMN last_name
            """))
            
            logger.info("✅ Rollback completed successfully!")
            
    except Exception as e:
        logger.error(f"❌ Rollback failed: {e}")
        raise


async def main():
    """Main migration function"""
    logger.info("=" * 60)
    logger.info("EdgeTrade Name Fields Migration")
    logger.info("=" * 60)
    
    if len(sys.argv) > 1 and sys.argv[1] == "--rollback":
        await rollback_migration()
    else:
        await migrate_name_fields()
    
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
