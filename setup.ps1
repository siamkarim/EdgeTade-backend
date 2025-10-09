# EdgeTrade FastAPI Setup Script (Windows PowerShell)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "EdgeTrade FastAPI Setup (Windows)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python (\d+\.\d+)") {
    $version = [Version]$matches[1]
    if ($version -lt [Version]"3.10") {
        Write-Host "❌ Python 3.10 or higher is required" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ $pythonVersion detected" -ForegroundColor Green
} else {
    Write-Host "❌ Python not found" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Create virtual environment
if (!(Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "⚠️  Virtual environment already exists" -ForegroundColor Yellow
}
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1
Write-Host "✅ Virtual environment activated" -ForegroundColor Green
Write-Host ""

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip
Write-Host "✅ pip upgraded" -ForegroundColor Green
Write-Host ""

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
Write-Host "✅ Dependencies installed" -ForegroundColor Green
Write-Host ""

# Check for .env file
if (!(Test-Path ".env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ .env file created" -ForegroundColor Green
        Write-Host "⚠️  Please edit .env with your configuration" -ForegroundColor Yellow
    } else {
        Write-Host "⚠️  .env.example not found" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️  .env file already exists" -ForegroundColor Yellow
}
Write-Host ""

# Check Docker
$dockerInstalled = Get-Command docker -ErrorAction SilentlyContinue
if ($dockerInstalled) {
    $startDocker = Read-Host "Docker detected. Start PostgreSQL in Docker? (y/n)"
    
    if ($startDocker -eq "y") {
        Write-Host "Starting PostgreSQL container..." -ForegroundColor Yellow
        docker run -d `
            --name edgetrade-db `
            -e POSTGRES_USER=edgetrade `
            -e POSTGRES_PASSWORD=edgetrade123 `
            -e POSTGRES_DB=edgetrade_db `
            -p 5432:5432 `
            postgres:14-alpine
        
        Write-Host "✅ PostgreSQL container started" -ForegroundColor Green
        Write-Host "Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
    }
} else {
    Write-Host "⚠️  Docker not found. Please install PostgreSQL manually" -ForegroundColor Yellow
}
Write-Host ""

# Initialize database
$initDb = Read-Host "Initialize the database? (y/n)"
if ($initDb -eq "y") {
    Write-Host "Initializing database..." -ForegroundColor Yellow
    python scripts/init_db.py
    Write-Host "✅ Database initialized" -ForegroundColor Green
    
    $createSample = Read-Host "Create sample data? (y/n)"
    if ($createSample -eq "y") {
        python scripts/create_sample_data.py
        Write-Host "✅ Sample data created" -ForegroundColor Green
    }
}
Write-Host ""

# Create logs directory
if (!(Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "✅ Logs directory created" -ForegroundColor Green
}
Write-Host ""

# Final message
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the application:" -ForegroundColor Yellow
Write-Host "  1. Activate virtual environment: .\venv\Scripts\Activate.ps1"
Write-Host "  2. Run the server: python main.py"
Write-Host ""
Write-Host "The API will be available at: http://localhost:8000"
Write-Host "API Documentation: http://localhost:8000/api/docs"
Write-Host ""
Write-Host "Admin credentials (change in production):"
Write-Host "  Email: admin@edgetrade.com"
Write-Host "  Password: admin123"
Write-Host ""
Write-Host "Happy trading! 🚀"

