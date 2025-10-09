"""
Database initialization script
Creates tables and optionally seeds initial data
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import Base, engine
from app.core.config import settings
from app.core.security import get_password_hash
from sqlalchemy import text
from loguru import logger


async def create_tables():
    """Create all database tables"""
    logger.info("Creating database tables...")
    
    # Import all models to ensure they're registered
    from app.models import user, trading_account, order, trade, audit_log
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    logger.info("✅ Tables created successfully")


async def seed_admin_user():
    """Create admin user if not exists"""
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.core.database import AsyncSessionLocal
    from app.models.user import User
    from sqlalchemy import select
    
    logger.info("Creating admin user...")
    
    async with AsyncSessionLocal() as session:
        # Check if admin exists
        result = await session.execute(
            select(User).where(User.email == settings.ADMIN_EMAIL)
        )
        existing_admin = result.scalar_one_or_none()
        
        if existing_admin:
            logger.info("Admin user already exists")
            return
        
        # Create admin user
        admin = User(
            email=settings.ADMIN_EMAIL,
            username="admin",
            hashed_password=get_password_hash(settings.ADMIN_PASSWORD),
            full_name="System Administrator",
            is_active=True,
            is_verified=True,
            is_admin=True,
        )
        
        session.add(admin)
        await session.commit()
        
        logger.info(f"✅ Admin user created: {settings.ADMIN_EMAIL}")


async def check_connection():
    """Check database connection"""
    logger.info("Checking database connection...")
    
    try:
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            result.fetchone()
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


async def main():
    """Main initialization function"""
    logger.info("=" * 60)
    logger.info("EdgeTrade Database Initialization")
    logger.info("=" * 60)
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[-1]}")
    logger.info("")
    
    # Check connection
    if not await check_connection():
        logger.error("Cannot proceed without database connection")
        return
    
    # Create tables
    await create_tables()
    
    # Seed admin user
    await seed_admin_user()
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("✅ Database initialization complete!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Admin credentials:")
    logger.info(f"  Email: {settings.ADMIN_EMAIL}")
    logger.info(f"  Password: {settings.ADMIN_PASSWORD}")
    logger.info("")
    logger.info("⚠️  IMPORTANT: Change the admin password in production!")
    logger.info("")


if __name__ == "__main__":
    asyncio.run(main())

