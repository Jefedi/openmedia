"""Configuration de l'application Celery"""
import os
from celery import Celery
from celery.schedules import crontab

# Configuration depuis l'environnement
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

CELERY_BROKER_URL = os.getenv(
    "CELERY_BROKER_URL",
    f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/1"
)
CELERY_RESULT_BACKEND = os.getenv(
    "CELERY_RESULT_BACKEND",
    f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/2"
)

# Créer l'application Celery
celery_app = Celery(
    "openmedia_worker",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=[
        "tasks.import_tasks",
        "tasks.sync_tasks",
        "tasks.maintenance_tasks",
    ]
)

# Configuration Celery
celery_app.conf.update(
    # Timezone
    timezone="UTC",
    enable_utc=True,

    # Sérialisation
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",

    # Résultats
    result_expires=3600,  # 1 heure
    result_extended=True,

    # Tâches
    task_track_started=True,
    task_time_limit=3600,  # 1 heure max par tâche
    task_soft_time_limit=3300,  # 55 minutes
    task_acks_late=True,  # Acknowledge après exécution
    task_reject_on_worker_lost=True,

    # Worker
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,

    # Retry
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,

    # Beat scheduler pour les tâches périodiques
    beat_schedule={
        # Mettre à jour les ratings chaque jour à 2h du matin
        "update-ratings-daily": {
            "task": "tasks.maintenance_tasks.update_media_ratings",
            "schedule": crontab(hour=2, minute=0),
        },
        # Nettoyer les tokens expirés chaque jour à 3h du matin
        "cleanup-expired-tokens": {
            "task": "tasks.maintenance_tasks.cleanup_expired_tokens",
            "schedule": crontab(hour=3, minute=0),
        },
        # Synchroniser avec les APIs externes chaque 6 heures
        "sync-external-data": {
            "task": "tasks.sync_tasks.sync_external_updates",
            "schedule": crontab(hour="*/6", minute=0),
        },
        # Mettre à jour l'index de recherche chaque heure
        "update-search-index": {
            "task": "tasks.maintenance_tasks.update_search_index",
            "schedule": crontab(minute=0),  # Toutes les heures
        },
    },
)

# Configuration de logging
celery_app.conf.update(
    worker_log_format="[%(asctime)s: %(levelname)s/%(processName)s] %(message)s",
    worker_task_log_format="[%(asctime)s: %(levelname)s/%(processName)s] [%(task_name)s(%(task_id)s)] %(message)s",
)


# Event handler pour le démarrage du worker
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    """Configurer les tâches périodiques supplémentaires si nécessaire"""
    pass


if __name__ == "__main__":
    celery_app.start()
