# svc-emergency-event-assessment

## 服务说明
- 服务名：`svc-emergency-event-assessment`
- 服务作用：模拟突发事件评估任务的计算负载服务
- 宿主机建议映射端口：`6010`
- 容器内部监听端口：`6000`（保持与现有模板一致）
- WINDOW_SIZE：`48`
- WORKLOAD_REPEAT：`18`
- INNER_ITERS：`260000`

## 接口
### 1) 健康检查
- `GET /health`

### 2) 单次推理
- `POST /infer_once`

请求体格式：
```json
{
  "task_id": "task_001",
  "source_node_id": "node1",
  "rows": [
    [0.0, 0.130787, 15.238246, 7.059044, 1.504443, 936.303039, 159.913899, 8.301527, 19.31548, 2.500038, 56.202419, 22.384064],
    [0.0, 0.139389, 14.83551, 7.121465, 1.388269, 923.238524, 121.215823, 9.569663, 17.478423, 2.369341, 70.122814, 19.418455]
  ]
}
```

返回字段（至少包含）：
- `status`
- `service`
- `exec_node_id`
- `source_node_id`
- `task_id`
- `rows`
- `feature_dim`
- `workload_repeat`
- `inner_iters`
- `score`
- `latency_s`

## 字段说明
原始数据集字段格式：

`ts,slot,node_id,rain_intensity_mmph,flow_m3s,temp_C,pH,DO_mgL,EC_uScm,COD_mgL,NH3N_mgL,TN_mgL,TP_mgL,TSS_mgL,turbidity_NTU`

实际微服务请求 `rows` 中只传以下 12 个特征，顺序固定为：

`rain_intensity_mmph, flow_m3s, temp_C, pH, DO_mgL, EC_uScm, COD_mgL, NH3N_mgL, TN_mgL, TP_mgL, TSS_mgL, turbidity_NTU`

示例原始数据（3 行）：
```text
2026-01-01 00:00:00,0,1,0.0,0.130787,15.238246,7.059044,1.504443,936.303039,159.913899,8.301527,19.31548,2.500038,56.202419,22.384064
2026-01-01 00:00:05,1,1,0.0,0.139389,14.83551,7.121465,1.388269,923.238524,121.215823,9.569663,17.478423,2.369341,70.122814,19.418455
2026-01-01 00:00:10,2,1,0.0,0.116323,15.373317,7.287082,1.63609,961.101525,115.72297,7.08381,18.04091,1.78673,72.313562,23.16212
```

## 使用示例
### curl
```bash
curl -X POST "http://127.0.0.1:6010/infer_once" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id":"task_001",
    "source_node_id":"node1",
    "rows":[
      [0.0,0.130787,15.238246,7.059044,1.504443,936.303039,159.913899,8.301527,19.31548,2.500038,56.202419,22.384064],
      [0.0,0.139389,14.83551,7.121465,1.388269,923.238524,121.215823,9.569663,17.478423,2.369341,70.122814,19.418455]
    ]
  }'
```

### docker build
```bash
docker build -t svc-emergency-event-assessment:latest .
```

### docker run
```bash
docker run -d --name svc-emergency-event-assessment -p 6010:6000 svc-emergency-event-assessment:latest
```
