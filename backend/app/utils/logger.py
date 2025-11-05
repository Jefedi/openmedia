"""Configuration du système de logging"""
import logging
import sys
from pathlib import Path

import structlog


def setup_logging(log_level: str = "INFO") -> structlog.BoundLogger:
    """
    Configure le système de logging avec structlog

    Args:
        log_level: Niveau de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Logger configuré
    """
    # Niveau de log
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Configuration des processeurs structlog
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # En développement, utiliser ConsoleRenderer pour une sortie lisible
    # En production, utiliser JSONRenderer pour parsing automatique
    if sys.stderr.isatty():
        processors.append(structlog.dev.ConsoleRenderer())
    else:
        processors.append(structlog.processors.JSONRenderer())

    # Configuration de structlog
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configuration du logging standard Python
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=level,
    )

    return structlog.get_logger()


# Créer le logger global
logger = setup_logging()


def get_logger(name: str = None) -> structlog.BoundLogger:
    """
    Obtenir un logger avec un nom spécifique

    Args:
        name: Nom du logger

    Returns:
        Logger configuré
    """
    if name:
        return structlog.get_logger(name)
    return logger
