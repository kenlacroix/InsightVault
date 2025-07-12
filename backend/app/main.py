from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import asyncio
from .auth import router as auth_router
from .api.files import router as files_router
from .api.chat import router as chat_router
from .api.settings import router as settings_router
from .database import init_db

app = FastAPI(
    title="InsightVault API",
    description="AI-Powered Personal Growth Assistant API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(files_router)
app.include_router(chat_router)
app.include_router(settings_router)

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup if tables don't exist."""
    try:
        print("[INFO] Checking database initialization...")
        await init_db()
        print("[SUCCESS] Database ready!")
    except Exception as e:
        print(f"[WARNING] Database initialization warning: {e}")
        print("[INFO] You may need to run 'python init_db.py' manually if issues persist.")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "InsightVault API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "insightvault-api",
        "version": "1.0.0"
    }

@app.get("/api/v1/health")
async def api_health():
    """API health check"""
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "message": "InsightVault API is running",
            "version": "1.0.0"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 