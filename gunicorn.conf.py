"""Gunicorn configuration for pipeline-metrics."""

import logging
import os
import sys
from threading import Event

from metrics.operator_repo_stats import CLONE_DIR, Scraper, load_configured_repos

bind = "0.0.0.0:8080"
workers = 1
timeout = 120
accesslog = "-"

_stop_event = Event()
_threads: list[Scraper] = []


def post_fork(server, worker):  # type: ignore[no-untyped-def]
    """Start background scraper threads in the worker process."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    root_logger = logging.getLogger("metrics")
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    repos_cfg = os.environ.get("METRICS_OPERATOR_REPOS_CFG_PATH", "repos.yml")
    for repo_name, repo_spec in load_configured_repos(repos_cfg).items():
        thread = Scraper(
            CLONE_DIR / repo_name,
            repo_spec["url"],
            _stop_event,
            repo_spec.get("branch"),
        )
        thread.start()
        _threads.append(thread)


def child_exit(server, worker):  # type: ignore[no-untyped-def]
    """Gracefully stop scraper threads when the worker exits."""
    _stop_event.set()
    for thread in _threads:
        thread.join()
