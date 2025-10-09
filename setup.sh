#!/bin/bash

# EdgeTrade FastAPI Setup Script
# This script sets up the entire development environment

set -e  # Exit on error

echo "========================================"
echo "EdgeTrade FastAPI Setup"
echo "========================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python 3.10+ is installed
echo "Checking Python version..."
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.10"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo -e "${RED}❌ Python 3.10 or higher is required${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python $PYTHON_VERSION detected${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✅ Virtual environment created${NC}"
else
    echo -e "${YELLOW}⚠️  Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate || . venv/Scripts/activate
echo -e "${GREEN}✅ Virtual environment activated${NC}"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip
echo -e "${GREEN}✅ pip upgraded${NC}"
echo ""

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
echo -e "${GREEN}✅ Dependencies installed${NC}"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file from example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo -e "${GREEN}✅ .env file created${NC}"
        echo -e "${YELLOW}⚠️  Please edit .env with your configuration${NC}"
    else
        echo -e "${YELLOW}⚠️  .env.example not found. You'll need to create .env manually${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  .env file already exists${NC}"
fi
echo ""

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "Docker detected. Would you like to start PostgreSQL in Docker? (y/n)"
    read -r START_DOCKER
    
    if [ "$START_DOCKER" = "y" ]; then
        echo "Starting PostgreSQL container..."
        docker run -d \
            --name edgetrade-db \
            -e POSTGRES_USER=edgetrade \
            -e POSTGRES_PASSWORD=edgetrade123 \
            -e POSTGRES_DB=edgetrade_db \
            -p 5432:5432 \
            postgres:14-alpine
        
        echo -e "${GREEN}✅ PostgreSQL container started${NC}"
        echo "Waiting for PostgreSQL to be ready..."
        sleep 5
    fi
else
    echo -e "${YELLOW}⚠️  Docker not found. Please install PostgreSQL manually${NC}"
fi
echo ""

# Initialize database
echo "Would you like to initialize the database? (y/n)"
read -r INIT_DB

if [ "$INIT_DB" = "y" ]; then
    echo "Initializing database..."
    python scripts/init_db.py
    echo -e "${GREEN}✅ Database initialized${NC}"
    
    echo ""
    echo "Would you like to create sample data? (y/n)"
    read -r CREATE_SAMPLE
    
    if [ "$CREATE_SAMPLE" = "y" ]; then
        python scripts/create_sample_data.py
        echo -e "${GREEN}✅ Sample data created${NC}"
    fi
fi
echo ""

# Create logs directory
mkdir -p logs
echo -e "${GREEN}✅ Logs directory created${NC}"
echo ""

# Final message
echo "========================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "========================================"
echo ""
echo "To start the application:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run the server: python main.py"
echo ""
echo "The API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/api/docs"
echo ""
echo "Admin credentials (change in production):"
echo "  Email: admin@edgetrade.com"
echo "  Password: admin123"
echo ""
echo "Sample user credentials:"
echo "  Email: demo1@example.com"
echo "  Password: Demo123456"
echo ""
echo "Happy trading! 🚀"

