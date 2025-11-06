#!/usr/bin/env python3
"""
Script pour créer toutes les tables de la base de données.
Utilisé pour l'initialisation initiale sans migrations Alembic.
"""
import sys
from sqlalchemy import create_engine

from app.config import settings
from app.models.base import Base

# Importer tous les modèles pour que SQLAlchemy les connaisse
from app.models.media import Movie, Series, Season, Episode, Genre, Person, Cast, Crew
from app.models.user import User, APIKey, RefreshToken
from app.models.tracking import UserWatchlist, UserHistory, UserProgress, UserRating
from app.models.availability import Platform, Availability


def create_tables() -> None:
    """Créer toutes les tables dans la base de données."""
    try:
        print("🔄 Création des tables dans la base de données...")

        # Créer le moteur de base de données
        engine = create_engine(
            str(settings.DATABASE_URL),
            pool_pre_ping=True,
        )

        # Créer toutes les tables
        Base.metadata.create_all(bind=engine)

        print("✅ Toutes les tables ont été créées avec succès !")
        print(f"")
        print(f"Tables créées :")
        for table_name in Base.metadata.tables.keys():
            print(f"  - {table_name}")

    except Exception as e:
        print(f"❌ Erreur lors de la création des tables: {e}")
        sys.exit(1)


if __name__ == "__main__":
    create_tables()
