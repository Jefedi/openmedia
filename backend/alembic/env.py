"""Configuration Alembic pour les migrations de base de données"""
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Configuration de l'application
import sys
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les modules
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import settings
from app.models.base import Base

# Importer tous les modèles pour Alembic
from app.models import *  # noqa: F401, F403

# Configuration Alembic
config = context.config

# Interpréter le fichier de config pour le logging Python
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Métadonnées de la base de données
target_metadata = Base.metadata

# URL de la base de données depuis les settings
config.set_main_option("sqlalchemy.url", str(settings.DATABASE_URL))


def run_migrations_offline() -> None:
    """
    Exécuter les migrations en mode 'offline'.

    Configure le contexte avec juste une URL et non un Engine,
    mais un Engine est également acceptable ici. En sautant la création
    du Engine, nous n'avons même pas besoin d'un DBAPI disponible.

    Les appels à context.execute() émettent ici la string SQL donnée
    vers le script de sortie.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Exécuter les migrations avec une connexion donnée"""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """
    Exécuter les migrations de manière asynchrone.

    Crée un Engine asynchrone et associe une connexion au contexte.
    """
    configuration = config.get_section(config.config_ini_section) or {}

    # URL de connexion
    configuration["sqlalchemy.url"] = str(settings.DATABASE_URL)

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Exécuter les migrations en mode 'online'."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
