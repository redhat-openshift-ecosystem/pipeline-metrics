"""Module for parsing operator repositories into useful metrics."""

import time
from pathlib import Path
import subprocess
from threading import Thread, Event

import yaml
from operator_repo import Repo

from metrics.prometheus_metrics import (
    MIGRATION_GAUGE,
    BUNDLES_IN_REPO_GAUGE,
    OPERATORS_IN_REPO_GAUGE,
    MIGRATION_COUNT_GAUGE,
)


CLONE_DIR = Path("/tmp")  # nosec
SYNC_DELAY = 86400  # 24 h in seconds


def ensure_repo(repo: Path, git_url: str) -> None:
    """Ensure a local repository exists and is up to date."""
    if repo.exists():
        pop = subprocess.Popen(
            ["git", "pull"],
            cwd=repo.absolute(),
        )
    else:
        # pylint: disable=consider-using-with
        pop = subprocess.Popen(["git", "clone", git_url, repo])
        # pylint: enable=consider-using-with
    pop.wait()


def load_configured_repos(config_path: Path | str = "repos.yml") -> dict[str, str]:
    """Load config file with repository names and remotes."""
    with open(config_path, "r", encoding="utf-8") as i_file:
        data: dict[str, str] = yaml.safe_load(i_file)
        return data


def parse_stats(repo: Path) -> None:
    """Parses stats for a single operator repository."""
    parsed_repo = Repo(repo)
    num_of_operators = 0
    migrated_operators = 0
    for operator in parsed_repo.all_operators():
        num_of_operators += 1
        if ci_content := operator.config:
            # We can check if this operator is migrated to FBC
            is_migrated = bool(ci_content.get("fbc", {}).get("enabled", False))
            migrated_operators += is_migrated
            MIGRATION_GAUGE.labels(
                repository=repo.name, operator=operator.operator_name
            ).set(int(is_migrated))
        BUNDLES_IN_REPO_GAUGE.labels(
            repository=repo.name, operator=operator.operator_name
        ).set(len(list(operator.all_bundles())))
    MIGRATION_COUNT_GAUGE.labels(repository=repo.name).set(migrated_operators)
    OPERATORS_IN_REPO_GAUGE.labels(repository=repo.name).set(num_of_operators)


class Scraper(Thread):
    """Class for a scraping worker."""

    def __init__(self, repo: Path, repo_url: str, stop_event: Event):
        super().__init__()
        self.repo = repo
        self.repo_url = repo_url
        self.stop_event = stop_event

    def run(self) -> None:
        tick = 0
        while not self.stop_event.is_set():
            # This way thread can be interrupted every second
            # but updates data only when delay interval is reached
            if not tick % SYNC_DELAY:
                ensure_repo(self.repo, self.repo_url)
                parse_stats(self.repo)
            tick += 1
            time.sleep(1)
