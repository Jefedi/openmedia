"""Database session configuration"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

# Créer le moteur de base de données
engine = create_engine(
    str(settings.DATABASE_URL),
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=settings.DB_POOL_PRE_PING,
    echo=settings.DB_ECHO,
)

# Créer la session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Générateur de session de base de données.
    Utilisé comme dépendance FastAPI.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
