#!/bin/bash

# EdgeTrade Backend - Quick Server Update Script
# Run this on your server to get the latest Swagger documentation

echo "🚀 EdgeTrade Backend - Server Update Script"
echo "============================================="

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "❌ Error: Please run this script from the EdgeTrade backend root directory"
    echo "   Current directory: $(pwd)"
    exit 1
fi

echo "📥 Pulling latest changes from GitHub..."
git pull origin master

if [ $? -eq 0 ]; then
    echo "✅ Code updated successfully!"
else
    echo "❌ Failed to pull latest changes"
    exit 1
fi

echo ""
echo "🔄 Restarting EdgeTrade service..."
supervisorctl restart edgetrade

if [ $? -eq 0 ]; then
    echo "✅ Service restarted successfully!"
else
    echo "❌ Failed to restart service"
    exit 1
fi

echo ""
echo "⏳ Waiting for service to start..."
sleep 5

echo ""
echo "🔍 Checking service status..."
supervisorctl status edgetrade

echo ""
echo "🎉 Server update completed!"
echo ""
echo "📚 Enhanced Swagger Documentation is now available:"
echo "   • Interactive Docs: https://yourdomain.com/api/docs"
echo "   • ReDoc: https://yourdomain.com/api/redoc"
echo "   • OpenAPI JSON: https://yourdomain.com/api/openapi.json"
echo ""
echo "🔧 New Features Available:"
echo "   • Comprehensive API documentation"
echo "   • Request/response examples"
echo "   • Error code documentation"
echo "   • Authentication guide"
echo "   • Trading flow examples"
echo "   • WebSocket documentation"
echo "   • SDK examples (JavaScript & Python)"
echo ""
echo "📖 Developer Documentation:"
echo "   • API Guide: API_DOCUMENTATION.md"
echo "   • Deployment Guide: DEPLOYMENT.md"
echo ""
echo "✅ Developers can now easily integrate with your platform!"
