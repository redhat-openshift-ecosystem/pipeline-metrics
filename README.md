# pipeline-metrics

Flask service that collects and exposes Prometheus metrics for operator pipelines.

**Metrics collected:**
- Pipeline run counts and durations (pushed by operator-pipelines Tekton tasks via `POST /v1/metrics/pipelinerun`)
- Operator repo statistics — operator counts, bundle counts, FBC migration status (scraped from git repos every 24h)

**Endpoints:**
- `GET /ping` — health check
- `GET /metrics` — Prometheus metrics
- `POST /v1/metrics/pipelinerun` — ingest pipeline run data

## Local development

### Run with podman

```bash
podman build -t pipeline-metrics .
podman run -p 8080:8080 -v ./repos.yml:/home/user/repos.yml:Z pipeline-metrics
```

### Run without container

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python setup.py install
metrics  # starts Flask dev server with scrapers
```

### Verify

```bash
curl http://localhost:8080/ping
curl http://localhost:8080/metrics
```

## Quality gates

```bash
pip install -r requirements-dev.txt
tox  # mypy, black, pylint, yamllint, bandit, pip-audit
```
