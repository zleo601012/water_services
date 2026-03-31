import os
import time
from typing import Dict, Any, List

import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel, Field


# =========================
# 服务基础配置
# =========================
SERVICE_NAME = os.getenv("SERVICE_NAME", "svc-pipe-blockage-risk")
NODE_ID = os.getenv("NODE_ID", "unknown")

# 这里代表这个服务默认处理的窗口长度
WINDOW_SIZE = int(os.getenv("WINDOW_SIZE", "12"))

# 负载参数
WORKLOAD_REPEAT = int(os.getenv("WORKLOAD_REPEAT", "6"))
INNER_ITERS = int(os.getenv("INNER_ITERS", "90000"))

# 当前服务使用的特征维度
FEATURE_DIM = 12

FEATURE_COLS = [
    "rain_intensity_mmph",
    "flow_m3s",
    "temp_C",
    "pH",
    "DO_mgL",
    "EC_uScm",
    "COD_mgL",
    "NH3N_mgL",
    "TN_mgL",
    "TP_mgL",
    "TSS_mgL",
    "turbidity_NTU",
]


# =========================
# 请求与响应模型
# =========================
class InferRequest(BaseModel):
    task_id: str = Field(..., description="任务ID")
    source_node_id: str = Field(..., description="原始任务来源节点")
    rows: List[List[float]] = Field(..., description="二维数组，每行一条记录，每列一个特征")
    workload_repeat: int | None = Field(default=None, description="可选，覆盖默认外层循环")
    inner_iters: int | None = Field(default=None, description="可选，覆盖默认内层循环")


class InferResponse(BaseModel):
    status: str
    service: str
    exec_node_id: str
    source_node_id: str
    task_id: str
    rows: int
    feature_dim: int
    workload_repeat: int
    inner_iters: int
    score: float
    latency_s: float


# =========================
# 工具函数
# =========================
def normalize_rows(x: np.ndarray) -> np.ndarray:
    mean = x.mean(axis=0, keepdims=True)
    std = x.std(axis=0, keepdims=True) + 1e-8
    return (x - mean) / std


def cpu_heavy_workload(feature_matrix: np.ndarray, repeat: int, inner_iters: int) -> float:
    """
    稳定版单次 CPU 计算负载
    目标：
    1. 单次执行较稳定
    2. 不依赖大型矩阵库预热
    3. 适合作为模拟微服务的“计算代价”
    """
    base_vec = feature_matrix.mean(axis=0).astype(np.float64)

    x = float(np.sum(base_vec) + 1.0)
    y = float(np.mean(base_vec) + 2.0)
    z = float(np.std(base_vec) + 3.0)

    acc = 0.0

    for r in range(repeat):
        v1 = x + r * 0.001
        v2 = y + r * 0.002
        v3 = z + r * 0.003

        for i in range(inner_iters):
            fi = i + 1.0

            a = v1 * 1.0000001 + fi * 0.0000005
            b = v2 * 0.9999999 + fi * 0.0000007
            c = v3 * 1.0000002 + fi * 0.0000006

            t1 = (a * b) / (abs(c) + 10.0)
            t2 = (b * c) / (abs(a) + 10.0)
            t3 = (c * a) / (abs(b) + 10.0)

            acc += t1 * 0.00031
            acc -= t2 * 0.00017
            acc += t3 * 0.00023

            acc += (a + b + c) * 0.00000001
            acc -= (a - b + c) * 0.000000007

            # 限幅，避免数值发散
            if acc > 1e6:
                acc = 1e6
            elif acc < -1e6:
                acc = -1e6

            v1 = a * 0.9999 + acc * 0.0000001
            v2 = b * 1.0001 - acc * 0.0000001
            v3 = c * 0.99995 + acc * 0.00000005

            if v1 > 1e4:
                v1 = 1e4
            elif v1 < -1e4:
                v1 = -1e4

            if v2 > 1e4:
                v2 = 1e4
            elif v2 < -1e4:
                v2 = -1e4

            if v3 > 1e4:
                v3 = 1e4
            elif v3 < -1e4:
                v3 = -1e4

    return float(acc / (repeat * inner_iters + 1e-8))


# =========================
# FastAPI
# =========================
app = FastAPI(title=SERVICE_NAME)


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": SERVICE_NAME,
        "node_id": NODE_ID,
        "window_size": WINDOW_SIZE,
        "feature_dim": FEATURE_DIM,
        "feature_cols": FEATURE_COLS,
        "workload_repeat": WORKLOAD_REPEAT,
        "inner_iters": INNER_ITERS,
    }


@app.post("/infer_once", response_model=InferResponse)
def infer_once(req: InferRequest) -> InferResponse:
    repeat = req.workload_repeat if req.workload_repeat is not None else WORKLOAD_REPEAT
    inner_iters = req.inner_iters if req.inner_iters is not None else INNER_ITERS

    x = np.array(req.rows, dtype=np.float64)

    if x.ndim != 2:
        raise ValueError("rows 必须是二维数组")

    if x.shape[0] <= 0:
        raise ValueError("rows 不能为空")

    if x.shape[1] != FEATURE_DIM:
        raise ValueError(f"每行特征数必须为 {FEATURE_DIM}，当前是 {x.shape[1]}")

    feature_matrix = normalize_rows(x)

    t0 = time.perf_counter()
    score = cpu_heavy_workload(feature_matrix, repeat=repeat, inner_iters=inner_iters)
    latency_s = time.perf_counter() - t0

    return InferResponse(
        status="ok",
        service=SERVICE_NAME,
        exec_node_id=str(NODE_ID),
        source_node_id=req.source_node_id,
        task_id=req.task_id,
        rows=int(x.shape[0]),
        feature_dim=int(x.shape[1]),
        workload_repeat=repeat,
        inner_iters=inner_iters,
        score=round(score, 6),
        latency_s=round(latency_s, 6),
    )