"""
Create sample data for testing
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.crud import user as user_crud, trading_account as account_crud
from app.schemas.user import UserCreate
from app.schemas.trading_account import TradingAccountCreate
from app.models.trading_account import AccountType, AccountCurrency
from loguru import logger


async def create_sample_users():
    """Create sample users for testing"""
    logger.info("Creating sample users...")
    
    async with AsyncSessionLocal() as session:
        # Sample users
        users_data = [
            {
                "email": "demo1@example.com",
                "username": "demo_trader1",
                "password": "Demo123456",
                "full_name": "Demo Trader One",
            },
            {
                "email": "demo2@example.com",
                "username": "demo_trader2",
                "password": "Demo123456",
                "full_name": "Demo Trader Two",
            },
        ]
        
        created_users = []
        for user_data in users_data:
            # Check if user exists
            existing = await user_crud.get_user_by_email(session, user_data["email"])
            if existing:
                logger.info(f"User {user_data['email']} already exists")
                created_users.append(existing)
                continue
            
            # Create user
            user = await user_crud.create_user(session, UserCreate(**user_data))
            logger.info(f"✅ Created user: {user.email}")
            created_users.append(user)
        
        return created_users


async def create_sample_accounts(users):
    """Create sample trading accounts"""
    logger.info("Creating sample trading accounts...")
    
    async with AsyncSessionLocal() as session:
        for user in users:
            # Demo account
            demo_account = await account_crud.create_trading_account(
                session,
                user.id,
                TradingAccountCreate(
                    account_name=f"{user.username} - Demo",
                    account_type=AccountType.DEMO,
                    currency=AccountCurrency.USD,
                    leverage=100,
                    initial_balance=10000.0,
                )
            )
            logger.info(f"✅ Created demo account: {demo_account.account_number}")
            
            # Live account
            live_account = await account_crud.create_trading_account(
                session,
                user.id,
                TradingAccountCreate(
                    account_name=f"{user.username} - Live",
                    account_type=AccountType.LIVE,
                    currency=AccountCurrency.USD,
                    leverage=500,
                    initial_balance=5000.0,
                )
            )
            logger.info(f"✅ Created live account: {live_account.account_number}")


async def main():
    """Main function"""
    logger.info("=" * 60)
    logger.info("Creating Sample Data")
    logger.info("=" * 60)
    logger.info("")
    
    # Create users
    users = await create_sample_users()
    
    # Create accounts
    await create_sample_accounts(users)
    
    logger.info("")
    logger.info("=" * 60)
    logger.info("✅ Sample data created successfully!")
    logger.info("=" * 60)
    logger.info("")
    logger.info("Sample user credentials:")
    logger.info("  Email: demo1@example.com")
    logger.info("  Password: Demo123456")
    logger.info("")
    logger.info("  Email: demo2@example.com")
    logger.info("  Password: Demo123456")
    logger.info("")


if __name__ == "__main__":
    asyncio.run(main())

