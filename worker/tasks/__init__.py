"""Tasks Celery pour OpenMedia"""
from tasks.celery_app import celery_app
from tasks.import_tasks import *  # noqa: F401, F403
from tasks.sync_tasks import *  # noqa: F401, F403
from tasks.maintenance_tasks import *  # noqa: F401, F403

__all__ = ["celery_app"]
