#!/usr/bin/env bash
# run pip-audit on dependencies, output to json file, mask any failures
pip-audit . --format=json -o /tmp/audit-output.json || true
