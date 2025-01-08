"""
Tekton metrics service that gathers and expose Prometheus metrics.
"""

import sys
from threading import Event
from typing import Any
import os
import logging

from flask import Flask, jsonify, request
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from metrics.operator_repo_stats import CLONE_DIR, load_configured_repos

from metrics.operator_repo_stats import Scraper
from metrics.prometheus_metrics import PIPELINERUN_COUNTER, PIPELINERUN_HISTOGRAM
from metrics.tekton import PipelineRun

app = Flask(__name__)


@app.route("/ping", methods=["GET"])
def ping() -> str:
    """
    Basic ping showing that the app is alive.
    """
    return "pong"


@app.route("/v1/metrics/pipelinerun", methods=["POST"])
def process_pipelinerun() -> Any:
    """
    Get a Tekton pipeline run summary and update Prometheus statistics

    Returns:
        Any: Response with metrics details
    """
    data = request.get_json()
    pipelinerun = PipelineRun(data)
    duration = pipelinerun.duration
    status = pipelinerun.status

    PIPELINERUN_COUNTER.labels(
        namespace=pipelinerun.namespace,
        pipeline=pipelinerun.pipeline_name,
        status=status,
    ).inc()

    PIPELINERUN_HISTOGRAM.labels(
        namespace=pipelinerun.namespace,
        pipeline=pipelinerun.pipeline_name,
        status=status,
    ).observe(duration)

    return jsonify(
        {
            "status": status,
            "pipeline": pipelinerun.pipeline_name,
            "pipelinerun_name": pipelinerun.pipelinerun_name,
            "duration": duration,
            "namespace": pipelinerun.namespace,
        }
    )


def init_metrics() -> Any:
    """
    Initialize API

    API is used to monitor and check the status tekton pipelines.

    """
    app.add_url_rule("/ping", view_func=ping)

    # Makes Prometheus metrics available on /metrics endpoint
    app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})

    return app


def main() -> None:
    """
    Main function
    """
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    root_logger = logging.getLogger("metrics")
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    init_metrics()
    stop_event = Event()
    threads = []
    for repo_name, repo_url in load_configured_repos(
        os.environ.get("METRICS_OPERATOR_REPOS_CFG_PATH", "repos.yml")
    ).items():
        thread = Scraper(CLONE_DIR / repo_name, repo_url, stop_event)
        thread.start()
        threads.append(thread)
    app.run(port=8080, host="0.0.0.0", debug=os.environ.get("DEBUG", False))  # nosec
    # Gracefully stop threads
    stop_event.set()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
