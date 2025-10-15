#!/usr/bin/env python3
"""
EdgeTrade Backend - Production Migration Runner
Run this script on your production server to apply all necessary migrations.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

async def run_migration(script_name, description):
    """Run a migration script"""
    print(f"\n🔄 Running {description}...")
    try:
        # Import and run the migration
        if script_name == "migrate_name_fields":
            from scripts.migrate_name_fields import migrate_name_fields
            await migrate_name_fields()
        elif script_name == "migrate_figma_fields":
            from scripts.migrate_figma_fields import run_migration
            await run_migration()
        elif script_name == "init_db":
            from scripts.init_db import main
            await main()
        else:
            print(f"❌ Unknown migration script: {script_name}")
            return False
        
        print(f"✅ {description} completed successfully!")
        return True
    except Exception as e:
        print(f"❌ {description} failed: {e}")
        return False

async def main():
    """Run all necessary migrations"""
    print("🚀 EdgeTrade Backend - Production Migration Runner")
    print("=" * 60)
    
    # Check if we're in the right directory
    if not os.path.exists("scripts/migrate_name_fields.py"):
        print("❌ Error: Please run this script from the EdgeTrade backend root directory")
        print("   Current directory:", os.getcwd())
        return 1
    
    migrations = [
        ("migrate_name_fields", "Name Fields Migration (full_name → first_name, last_name)"),
        ("migrate_figma_fields", "Figma Fields Migration (id_number, date_of_birth, verification codes)"),
        ("init_db", "Database Initialization (create tables, admin user)"),
    ]
    
    print("📋 Migration Plan:")
    for i, (script, desc) in enumerate(migrations, 1):
        print(f"   {i}. {desc}")
    
    print("\n⚠️  WARNING: This will modify your production database!")
    response = input("Do you want to continue? (yes/no): ").lower().strip()
    
    if response not in ['yes', 'y']:
        print("❌ Migration cancelled by user")
        return 1
    
    print("\n🔄 Starting migrations...")
    
    results = []
    for script_name, description in migrations:
        result = await run_migration(script_name, description)
        results.append((description, result))
        
        if not result:
            print(f"\n❌ Migration failed: {description}")
            print("🛑 Stopping migration process")
            break
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 MIGRATION SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for description, result in results:
        status = "✅ SUCCESS" if result else "❌ FAILED"
        print(f"{status} {description}")
        if result:
            passed += 1
    
    print(f"\n📈 Results: {passed}/{total} migrations completed")
    
    if passed == total:
        print("🎉 All migrations completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Restart your EdgeTrade service: supervisorctl restart edgetrade")
        print("   2. Run deployment verification: python verify_deployment.py")
        print("   3. Test the API endpoints")
        return 0
    else:
        print("⚠️  Some migrations failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Migration interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Migration failed with error: {e}")
        sys.exit(1)
