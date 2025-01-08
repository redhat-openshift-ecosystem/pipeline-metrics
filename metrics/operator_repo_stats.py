"""Module for parsing operator repositories into useful metrics."""

import time
from pathlib import Path
import subprocess
from threading import Thread, Event

import yaml

from metrics.prometheus_metrics import (
    MIGRATION_GAUGE,
    BUNDLES_IN_REPO_GAUGE,
    OPERATORS_IN_REPO_GAUGE,
    MIGRATION_COUNT_GAUGE,
)


CLONE_DIR = Path("/tmp")  # nosec
OPERATORS_DIR_NAME = "operators"
CI_FILE_NAME = "ci.yaml"
SYNC_DELAY = 86400  # 24 h in seconds


def ensure_repo(repo: Path, git_url: str) -> None:
    """Ensure a local repository exists and is up to date."""
    if repo.exists():
        pop = subprocess.Popen(
            ["cd", repo.absolute(), ";", "git", "pull"], shell=True
        )  # nosec
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
    operators_dir = repo / OPERATORS_DIR_NAME
    if operators_dir.exists() and operators_dir.is_dir():
        num_of_operators = 0
        migrated_operators = 0
        for operator in operators_dir.iterdir():
            if not operator.is_dir():
                # The directory can also contain files like README
                continue
            ci_file = operator / CI_FILE_NAME
            if not ci_file.exists():
                continue
            # This is an operator
            num_of_operators += 1
            # Update number of bundles
            BUNDLES_IN_REPO_GAUGE.labels(
                repository=repo.name, operator=operator.name
            ).set(len([x for x in operator.iterdir() if x.is_dir()]))
            # Update FBC status
            with open(ci_file, "r", encoding="utf-8") as read_file:
                data = yaml.safe_load(read_file)
                is_migrated: bool = bool(data.get("fbc", {}).get("enabled", False))
                migrated_operators += is_migrated
                MIGRATION_GAUGE.labels(
                    repository=repo.name, operator=operator.name
                ).set(int(is_migrated))
        OPERATORS_IN_REPO_GAUGE.labels(repository=repo.name).set(num_of_operators)
        MIGRATION_COUNT_GAUGE.labels(repository=repo.name).set(migrated_operators)


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
