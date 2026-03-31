#!/usr/bin/env bash
set -euo pipefail

export SERVICE_NAME=${SERVICE_NAME:-svc-pipe-blockage-risk}
export NODE_ID=${NODE_ID:-local-node}
export WINDOW_SIZE=${WINDOW_SIZE:-12}
export WORKLOAD_REPEAT=${WORKLOAD_REPEAT:-6}
export INNER_ITERS=${INNER_ITERS:-90000}

uvicorn app.main:app --host 0.0.0.0 --port 6000
