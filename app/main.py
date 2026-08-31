from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.database import create_tables
from app.api.auth import router as auth_router
from app.api.widgets import router as widget_router
from app.api.submissions import router as submission_router
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Lead Capture Platform",
    description="Embeddable Widget & Lead-Capture Platform API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Configure CORS - Allow all for public endpoints
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for public submissions
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,  # Cache preflight requests for 1 hour
)

# Add trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*"]
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(widget_router, prefix="/api")
app.include_router(submission_router, prefix="/api")

# Serve static files (widget.js)
app.mount("/", StaticFiles(directory="app/static", html=True), name="static")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Lead Capture Platform API",
        "version": "1.0.0",
        "status": "running"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "lead-capture-api"
    }

# Create tables on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application...")
    create_tables()
    logger.info("Application startup complete")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application...")
