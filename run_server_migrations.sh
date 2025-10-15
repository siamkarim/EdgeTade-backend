#!/bin/bash

# EdgeTrade Backend - Server Migration Script
# Run this script on your production server to apply all migrations

echo "🚀 EdgeTrade Backend - Production Migration Script"
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "scripts/migrate_name_fields.py" ]; then
    echo "❌ Error: Please run this script from the EdgeTrade backend root directory"
    echo "   Current directory: $(pwd)"
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

echo "📋 Migration Plan:"
echo "   1. Name Fields Migration (full_name → first_name, last_name)"
echo "   2. Figma Fields Migration (id_number, date_of_birth, verification codes)"
echo "   3. Database Initialization (create tables, admin user)"
echo ""

echo "⚠️  WARNING: This will modify your production database!"
read -p "Do you want to continue? (yes/no): " response

if [[ ! "$response" =~ ^(yes|y)$ ]]; then
    echo "❌ Migration cancelled by user"
    exit 1
fi

echo ""
echo "🔄 Starting migrations..."

# Migration 1: Name Fields
echo ""
echo "🔄 Running Name Fields Migration..."
python3 scripts/migrate_name_fields.py
if [ $? -eq 0 ]; then
    echo "✅ Name Fields Migration completed successfully!"
else
    echo "❌ Name Fields Migration failed!"
    exit 1
fi

# Migration 2: Figma Fields
echo ""
echo "🔄 Running Figma Fields Migration..."
python3 scripts/migrate_figma_fields.py
if [ $? -eq 0 ]; then
    echo "✅ Figma Fields Migration completed successfully!"
else
    echo "❌ Figma Fields Migration failed!"
    exit 1
fi

# Migration 3: Database Initialization
echo ""
echo "🔄 Running Database Initialization..."
python3 scripts/init_db.py
if [ $? -eq 0 ]; then
    echo "✅ Database Initialization completed successfully!"
else
    echo "❌ Database Initialization failed!"
    exit 1
fi

echo ""
echo "🎉 All migrations completed successfully!"
echo ""
echo "📝 Next steps:"
echo "   1. Restart your EdgeTrade service: supervisorctl restart edgetrade"
echo "   2. Check service status: supervisorctl status edgetrade"
echo "   3. Test the API endpoints"
echo "   4. Visit API documentation: https://yourdomain.com/api/docs"
echo ""
echo "🔍 To verify deployment, run: python3 verify_deployment.py"
