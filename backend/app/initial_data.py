#!/usr/bin/env python3
"""
Script pour créer les données initiales de l'application.

NOTE: L'utilisateur admin n'est plus créé automatiquement.
Le premier utilisateur à s'enregistrer devient automatiquement le propriétaire/admin du site.
"""
import sys
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.user import User


def init_db() -> None:
    """Initialiser la base de données avec les données de base."""
    db = SessionLocal()
    try:
        # Vérifier le nombre d'utilisateurs
        user_count = db.query(User).count()

        if user_count > 0:
            print(f"✅ Base de données déjà initialisée ({user_count} utilisateur(s))")
        else:
            print(f"ℹ️  Aucun utilisateur trouvé")
            print(f"")
            print(f"👤 Le premier utilisateur à s'enregistrer deviendra le propriétaire/admin du site")
            print(f"")
            print(f"📝 Pour créer votre compte admin, visitez: http://localhost:3000/register")
            print(f"")

    except Exception as e:
        print(f"❌ Erreur lors de la vérification de la base de données: {e}")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    print("🔄 Initialisation des données...")
    init_db()
    print("✅ Initialisation terminée")
