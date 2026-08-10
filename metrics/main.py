"""
Tekton metrics service that gathers and expose Prometheus metrics.
"""

from typing import Any

from flask import Flask, jsonify, request
from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

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


# Makes Prometheus metrics available on /metrics endpoint
app.wsgi_app = DispatcherMiddleware(app.wsgi_app, {"/metrics": make_wsgi_app()})
