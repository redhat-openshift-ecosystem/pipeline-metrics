"""Prometheus metrics"""

from prometheus_client import Counter, Histogram, Gauge

PIPELINERUN_COUNTER = Counter(
    "isv_pipelinerun_counter",
    "ISV pipeline run counter.",
    ["pipeline", "status", "namespace"],
)

PIPELINERUN_HISTOGRAM = Histogram(
    "isv_pipelinerun_duration_seconds",
    "ISV pipeline duration histogram",
    ["pipeline", "status", "namespace"],
    buckets=(60, 5 * 60, 10 * 60, 20 * 60, 40 * 60, 50 * 60, 60 * 60),
)

MIGRATION_GAUGE = Gauge(
    "operator_migration_status",
    "Status of migration to FBC of an Operator.",
    ["repository", "operator"],
)

MIGRATION_COUNT_GAUGE = Gauge(
    "migrated_operators", "Number of migrated operators", ["repository"]
)

OPERATORS_IN_REPO_GAUGE = Gauge(
    "operators_in_repository", "Number of operators in a repository.", ["repository"]
)

BUNDLES_IN_REPO_GAUGE = Gauge(
    "bundles_in_repository",
    "Number of bundles in a repository",
    ["repository", "operator"],
)
