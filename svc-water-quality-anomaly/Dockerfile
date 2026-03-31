FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app

ENV SERVICE_NAME=svc-water-quality-anomaly
ENV NODE_ID=unknown
ENV WINDOW_SIZE=24
ENV WORKLOAD_REPEAT=12
ENV INNER_ITERS=180000

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "6000"]