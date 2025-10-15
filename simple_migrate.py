#!/usr/bin/env python3
"""
Simple Migration Script for EdgeTrade Backend
Run this directly on your production server
"""

import asyncio
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

async def run_all_migrations():
    """Run all migrations in sequence"""
    print("🚀 EdgeTrade Backend - Simple Migration Runner")
    print("=" * 50)
    
    try:
        # Migration 1: Name Fields
        print("\n🔄 Running Name Fields Migration...")
        from scripts.migrate_name_fields import migrate_name_fields
        await migrate_name_fields()
        print("✅ Name Fields Migration completed!")
        
        # Migration 2: Figma Fields
        print("\n🔄 Running Figma Fields Migration...")
        from scripts.migrate_figma_fields import run_migration
        await run_migration()
        print("✅ Figma Fields Migration completed!")
        
        # Migration 3: Database Initialization
        print("\n🔄 Running Database Initialization...")
        from scripts.init_db import main
        await main()
        print("✅ Database Initialization completed!")
        
        print("\n🎉 All migrations completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Restart your EdgeTrade service: supervisorctl restart edgetrade")
        print("   2. Check service status: supervisorctl status edgetrade")
        print("   3. Test the API: python verify_deployment.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(run_all_migrations())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Migration failed with error: {e}")
        sys.exit(1)
