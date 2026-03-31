#!/usr/bin/env bash
set -euo pipefail

export SERVICE_NAME=${SERVICE_NAME:-svc-water-quality-anomaly}
export NODE_ID=${NODE_ID:-local-node}
export WINDOW_SIZE=${WINDOW_SIZE:-24}
export WORKLOAD_REPEAT=${WORKLOAD_REPEAT:-12}
export INNER_ITERS=${INNER_ITERS:-180000}

uvicorn app.main:app --host 0.0.0.0 --port 6000
