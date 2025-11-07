"""Application principale OpenMedia API"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from pathlib import Path

from app.config import settings
from app.utils.logger import logger
from app.routes import api_router

# Import des modèles pour Alembic
from app.models import *  # noqa: F401, F403


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Cycle de vie de l'application"""
    # Startup
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Create uploads directories
    uploads_dir = Path("/app/uploads")
    avatars_dir = uploads_dir / "avatars"
    try:
        avatars_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Uploads directory ready: {uploads_dir}")
    except Exception as e:
        logger.error(f"Failed to create uploads directory: {e}")

    # TODO: Initialiser les connexions DB, Redis, Meilisearch
    # await init_db()
    # await init_redis()
    # await init_search()

    yield

    # Shutdown
    logger.info("Shutting down application")
    # TODO: Fermer les connexions
    # await close_db()
    # await close_redis()
    # await close_search()


# Création de l'application FastAPI
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API open-source pour la gestion et le suivi de films/séries",
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    docs_url=f"{settings.API_V1_PREFIX}/docs",
    redoc_url=f"{settings.API_V1_PREFIX}/redoc",
    lifespan=lifespan,
)


# =============================================================================
# MIDDLEWARES
# =============================================================================

# CORS - Cross-Origin Resource Sharing
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Total-Count", "X-Page", "X-Per-Page"],
    )

# Trusted Host - Protection contre les attaques Host header
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # TODO: Configurer les hosts autorisés
    )


# =============================================================================
# SECURITY HEADERS MIDDLEWARE
# =============================================================================

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Ajouter les headers de sécurité à toutes les réponses"""
    response = await call_next(request)

    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

    # Content Security Policy
    if settings.ENVIRONMENT == "production":
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self';"
        )

    return response


# =============================================================================
# LOGGING MIDDLEWARE
# =============================================================================

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Logger toutes les requêtes"""
    logger.info(
        f"Request: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else None,
        }
    )

    response = await call_next(request)

    logger.info(
        f"Response: {response.status_code}",
        extra={
            "status_code": response.status_code,
            "method": request.method,
            "path": request.url.path,
        }
    )

    return response


# =============================================================================
# EXCEPTION HANDLERS
# =============================================================================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Gérer les exceptions HTTP"""
    logger.warning(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "detail": exc.detail,
            "path": request.url.path,
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.status_code,
                "message": exc.detail,
                "type": "http_error"
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Gérer les erreurs de validation"""
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={
            "errors": exc.errors(),
            "path": request.url.path,
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": 422,
                "message": "Validation error",
                "type": "validation_error",
                "details": exc.errors()
            }
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Gérer toutes les autres exceptions"""
    logger.error(
        f"Unexpected error: {str(exc)}",
        extra={
            "error": str(exc),
            "type": type(exc).__name__,
            "path": request.url.path,
        },
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": 500,
                "message": "Internal server error" if settings.ENVIRONMENT == "production" else str(exc),
                "type": "internal_error"
            }
        },
    )


# =============================================================================
# ROUTES
# =============================================================================

@app.get("/health", tags=["Health"])
async def health_check():
    """Vérifier l'état de santé de l'API"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/", tags=["Root"])
async def root():
    """Route racine"""
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_PREFIX}/docs",
    }


# Enregistrer les routes API
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory="/app/uploads"), name="uploads")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
