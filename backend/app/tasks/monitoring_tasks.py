"""Monitoring Celery tasks (stubs)."""

import logging

from app.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.monitoring_tasks.scan_local_folder")
def scan_local_folder(folder_path: str, user_id: str):
    """Scan a local folder and index new files (stub)."""
    logger.info(f"[STUB] Scanning folder {folder_path} for user {user_id}")
    return {"status": "stub", "folder": folder_path, "files_found": 0}


@celery_app.task(name="app.tasks.monitoring_tasks.run_scheduled_search")
def run_scheduled_search():
    """Run all active scheduled searches (stub)."""
    logger.info("[STUB] Running scheduled searches")
    return {"status": "stub", "tasks_run": 0}
