"""
Tekton metrics service that gathers and expose Prometheus metrics.
"""
from typing import Any
import os

from flask import Flask, jsonify, request
from prometheus_client import Counter, Histogram, make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from metrics.tekton import PipelineRun

app = Flask(__name__)

# Prometheus metrics
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


@app.route("/ping", methods=["GET"])
def ping() -> str:
    """
    Basic ping showing that the app is alive.
    """
    return "pong"


@app.route("/v1/metrics/pipelinerun", methods=["POST"])
def process_pipelinerun() -> Any:
    """
    Get a Tenton pipeline run summary and update Prometherus statistics

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
    init_metrics()
    app.run(port=8080, host="0.0.0.0", debug=os.environ.get("DEBUG", False))  # nosec


if __name__ == "__main__":
    main()
