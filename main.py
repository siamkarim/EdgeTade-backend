"""
EdgeTrade FastAPI Trading Platform
Main application entry point
"""
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    # Debug: Print configuration to verify .env loading
    print(f"Configuration loaded:")
    print(f"   Database URL: {settings.DATABASE_URL}")
    print(f"   CORS Origins: {settings.cors_origins_list}")
    print(f"   Environment: {settings.ENVIRONMENT}")
    print(f"   Debug Mode: {settings.DEBUG}")
    print(f"   Host: {settings.HOST}:{settings.PORT}")
    print("=" * 50)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )

