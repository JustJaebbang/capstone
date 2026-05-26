"""APScheduler integration for daily collection batch.

Lifecycle:
- `init_scheduler()` — called from FastAPI lifespan startup
- `shutdown_scheduler()` — called from FastAPI lifespan shutdown
- `trigger_refresh_now()` — manual one-shot trigger for testing

uvicorn --reload guard:
- toclaude2 §"스케줄러 구조" flags the double-execution risk
- We guard via `settings.scheduler_enabled` (set false in dev/tests via .env)
- Lifespan only fires once per process, so reload child runs scheduler;
  reloader parent doesn't run lifespan
"""
from __future__ import annotations

import logging
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings
from app.services import collection_service

logger = logging.getLogger(__name__)

NIGHTLY_REFRESH_JOB_ID = "nightly_collection_refresh"

_scheduler: Optional[BackgroundScheduler] = None


def init_scheduler() -> Optional[BackgroundScheduler]:
    """Idempotent scheduler startup. Returns the scheduler or None if disabled."""
    global _scheduler
    if not settings.scheduler_enabled:
        logger.info("scheduler disabled via settings.scheduler_enabled")
        return None
    if _scheduler is not None:
        logger.warning("scheduler already initialized; skipping")
        return _scheduler

    _scheduler = BackgroundScheduler(timezone=settings.scheduler_timezone)
    _scheduler.add_job(
        collection_service.refresh_all_subscribed_movies,
        trigger=CronTrigger(
            hour=settings.collection_cron_hour,
            minute=settings.collection_cron_minute,
        ),
        id=NIGHTLY_REFRESH_JOB_ID,
        replace_existing=True,
        misfire_grace_time=3600,  # 1h tolerance for missed runs (sleep/restart)
    )
    _scheduler.start()
    logger.info(
        "scheduler started: refresh at %02d:%02d %s",
        settings.collection_cron_hour,
        settings.collection_cron_minute,
        settings.scheduler_timezone,
    )
    return _scheduler


def shutdown_scheduler() -> None:
    """Stop the scheduler if running. Safe to call multiple times."""
    global _scheduler
    if _scheduler is None:
        return
    try:
        _scheduler.shutdown(wait=False)
        logger.info("scheduler shut down")
    except Exception as exc:
        logger.warning("scheduler shutdown error: %s", exc)
    finally:
        _scheduler = None


def trigger_refresh_now() -> dict[str, int]:
    """Run the refresh job synchronously, ignoring schedule. For manual testing."""
    return collection_service.refresh_all_subscribed_movies(mode="scheduled")


def get_next_run_time() -> Optional[str]:
    """Inspection helper. Returns ISO string of next scheduled run, or None."""
    if _scheduler is None:
        return None
    job = _scheduler.get_job(NIGHTLY_REFRESH_JOB_ID)
    if job is None or job.next_run_time is None:
        return None
    return job.next_run_time.isoformat()
