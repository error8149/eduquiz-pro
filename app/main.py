import logging
import os
from logging.handlers import RotatingFileHandler

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .routers import error_router, history, quiz_router
from .config import settings, log_config
from .database import check_database_health

# Setup logging
logger = logging.getLogger(__name__)

def setup_logging():
    """Configure application logging"""
    handlers = []
    
    # Console handler
    if log_config.ENABLE_CONSOLE:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_config.LEVEL)
        console_handler.setFormatter(logging.Formatter(log_config.FORMAT))
        handlers.append(console_handler)
    
    # File handler
    if log_config.ENABLE_FILE:
        file_handler = RotatingFileHandler(
            log_config.FILE, 
            maxBytes=log_config.MAX_BYTES, 
            backupCount=log_config.BACKUP_COUNT
        )
        file_handler.setLevel(log_config.LEVEL)
        file_handler.setFormatter(logging.Formatter(log_config.FORMAT))
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=log_config.LEVEL,
        format=log_config.FORMAT,
        handlers=handlers
    )

# Initialize logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# CORS middleware
logger.info("Initializing CORS middleware")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Received {request.method} request for {request.url.path} from {request.client.host}")
    if settings.DEBUG:
        logger.debug(f"Headers: {dict(request.headers)}")
    try:
        response = await call_next(request)
        logger.info(f"Responded with status {response.status_code} for {request.url.path}")
        return response
    except Exception as e:
        logger.error(f"Error processing {request.method} {request.url.path}: {str(e)}", exc_info=True)
        return JSONResponse(status_code=500, content={"detail": f"Internal server error: {str(e)}"})

# Explicit OPTIONS handler for all API routes
@app.options(f"{settings.API_V1_PREFIX}/{{path:path}}")
async def options_handler(request: Request):
    logger.info(f"Handling OPTIONS request for {request.url.path} from {request.client.host}")
    return JSONResponse(
        content={"status": "ok"},
        headers={
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Methods": ",".join(settings.CORS_ALLOW_METHODS),
            "Access-Control-Allow-Headers": ",".join(settings.CORS_ALLOW_HEADERS),
            "Access-Control-Max-Age": "86400",
        }
    )

# Include routers
logger.info("Including routers")
try:
    app.include_router(quiz_router, prefix=settings.API_V1_PREFIX, tags=["Quiz"])
    app.include_router(error_router, prefix=settings.API_V1_PREFIX, tags=["Error"])
    app.include_router(history, prefix=settings.API_V1_PREFIX, tags=["History"])
except Exception as e:
    logger.error(f"Failed to include routers: {str(e)}", exc_info=True)
    raise

# Mount static files
frontend_path = os.path.join(os.path.dirname(__file__), "..", settings.FRONTEND_DIR)
if not os.path.exists(frontend_path):
    logger.error(f"Frontend directory not found at {frontend_path}")
    raise RuntimeError(f"Frontend directory not found at {frontend_path}")

app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

@app.get("/")
async def root():
    logger.info("Serving root endpoint: index.html")
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/health")
async def health_check():
    logger.info("Health check requested")
    db_healthy = check_database_health()
    return {
        "status": "healthy" if db_healthy else "unhealthy", 
        "database": "connected" if db_healthy else "disconnected",
        "environment": settings.ENVIRONMENT,
        "version": settings.APP_VERSION,
        "debug": settings.DEBUG
    }

@app.get("/config")
async def get_config():
    """Get public configuration for frontend"""
    return {
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "api_base_url": settings.API_V1_PREFIX,
        "max_questions": settings.MAX_QUESTIONS_PER_QUIZ,
        "min_questions": settings.MIN_QUESTIONS_PER_QUIZ,
        "supported_providers": settings.SUPPORTED_AI_PROVIDERS,
        "features": {
            "history": settings.ENABLE_HISTORY,
            "export": settings.ENABLE_EXPORT,
            "ai_explanations": settings.ENABLE_AI_EXPLANATIONS,
            "manual_mode": settings.ENABLE_MANUAL_MODE,
        }
    }

@app.on_event("startup")
async def startup_event():
    logger.info(f"{settings.APP_NAME} v{settings.APP_VERSION} started in {settings.ENVIRONMENT} mode")
    logger.info(f"Debug mode: {settings.DEBUG}")
    logger.info(f"Database: {settings.DATABASE_URL}")
    logger.info(f"Host: {settings.HOST}:{settings.PORT}")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"{settings.APP_NAME} shutting down")