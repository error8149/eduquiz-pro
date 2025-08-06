import logging
import os
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routers import error_router, history, quiz_router

# Setup logging based on configuration
def setup_logging():
    """Configure logging based on settings"""
    log_handlers = [logging.StreamHandler()]
    
    # Add file handler only in development or if explicitly configured
    if settings.is_development and settings.log_file:
        try:
            file_handler = RotatingFileHandler(
                settings.log_file,
                maxBytes=settings.log_max_size,
                backupCount=settings.log_backup_count
            )
            log_handlers.append(file_handler)
        except Exception as e:
            print(f"Warning: Could not setup file logging: {e}")
    
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=log_handlers,
        force=True
    )

setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info(f"🚀 Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"🌍 Environment: {settings.environment}")
    logger.info(f"🗄️  Database: {settings.database_url[:30]}...")
    logger.info(f"🔗 Base URL: {settings.base_url}")
    logger.info(f"🎯 API Endpoint: {settings.base_url}{settings.api_base_url}")
    
    yield
    
    # Shutdown
    logger.info(f"⚡ Shutting down {settings.app_name}")

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-Powered Quiz Platform for Exam Preparation",
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
logger.info("🔒 Configuring CORS middleware")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=settings.cors_max_age,
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log requests and handle errors"""
    if settings.debug:
        client_ip = request.client.host if request.client else "unknown"
        logger.info(f"📥 {request.method} {request.url.path} from {client_ip}")
    
    try:
        response = await call_next(request)
        
        if settings.debug:
            logger.info(f"📤 Response: {response.status_code}")
        
        return response
        
    except Exception as e:
        logger.error(f"❌ Error processing {request.method} {request.url.path}: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )

# Enhanced OPTIONS handler
@app.options("/{path:path}")
async def options_handler(request: Request):
    """Handle CORS preflight requests"""
    origin = request.headers.get("origin", "*")
    
    return JSONResponse(
        content={"status": "ok"},
        headers={
            "Access-Control-Allow-Origin": origin if origin in settings.allowed_origins else "*",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Max-Age": str(settings.cors_max_age),
            "Access-Control-Allow-Credentials": "true" if settings.cors_allow_credentials else "false",
        }
    )

# Include API routers
logger.info("📚 Including API routers")
app.include_router(quiz_router, prefix=settings.api_base_url, tags=["Quiz"])
app.include_router(error_router, prefix=settings.api_base_url, tags=["Error"])
app.include_router(history, prefix=settings.api_base_url, tags=["History"])

# Static files setup
frontend_path = os.path.join(os.path.dirname(__file__), "..", settings.frontend_path)
if os.path.exists(frontend_path):
    app.mount(settings.static_url, StaticFiles(directory=frontend_path), name="static")
    logger.info(f"📁 Static files mounted from: {frontend_path}")
else:
    logger.warning(f"⚠️  Frontend directory not found: {frontend_path}")

@app.get("/")
async def root():
    """Serve the main application page"""
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    
    return {
        "message": f"Welcome to {settings.app_name} API",
        "version": settings.app_version,
        "environment": settings.environment,
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
        "api": f"{settings.api_base_url}",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": __import__('datetime').datetime.utcnow().isoformat()
    }

@app.get("/config")
async def get_client_config():
    """Get client-side configuration"""
    return {
        "api_base_url": settings.api_base_url,
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "base_url": settings.base_url,
        "defaults": {
            "ai_provider": settings.default_ai_provider,
            "grade_level": settings.default_grade_level,
            "difficulty": settings.default_difficulty,
            "num_questions": settings.default_num_questions,
            "time_limit": settings.default_time_limit
        }
    }

if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"🚀 Starting server on {settings.host}:{settings.port}")
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
        access_log=settings.debug
    )