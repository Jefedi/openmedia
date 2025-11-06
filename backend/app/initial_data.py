#!/usr/bin/env python3
"""
Script pour créer les données initiales de l'application.
Crée l'utilisateur admin si nécessaire.
"""
import sys
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from app.db.session import SessionLocal
from app.models.user import User
from app.config import settings

# Contexte de hashing des mots de passe
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")


def init_db() -> None:
    """Initialiser la base de données avec les données de base."""
    db = SessionLocal()
    try:
        # Vérifier si l'utilisateur admin existe déjà
        admin = db.query(User).filter(User.email == settings.FIRST_SUPERUSER_EMAIL).first()

        if admin:
            print(f"✅ Utilisateur admin existe déjà: {settings.FIRST_SUPERUSER_EMAIL}")
            return

        # Créer l'utilisateur admin
        print(f"👤 Création de l'utilisateur admin: {settings.FIRST_SUPERUSER_EMAIL}")

        admin = User(
            email=settings.FIRST_SUPERUSER_EMAIL,
            username="admin",
            hashed_password=pwd_context.hash(settings.FIRST_SUPERUSER_PASSWORD),
            full_name="Administrator",
            is_active=True,
            is_superuser=True,
            is_verified=True,
        )

        db.add(admin)
        db.commit()
        db.refresh(admin)

        print(f"✅ Utilisateur admin créé avec succès !")
        print(f"")
        print(f"📧 Email: {settings.FIRST_SUPERUSER_EMAIL}")
        print(f"🔑 Mot de passe: {settings.FIRST_SUPERUSER_PASSWORD}")
        print(f"")
        print(f"⚠️  IMPORTANT: Changez ce mot de passe après la première connexion !")

    except Exception as e:
        print(f"❌ Erreur lors de la création de l'utilisateur admin: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("🔄 Initialisation des données...")
    init_db()
    print("✅ Initialisation terminée")
