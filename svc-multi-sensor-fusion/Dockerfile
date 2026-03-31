FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app

ENV SERVICE_NAME=svc-multi-sensor-fusion
ENV NODE_ID=unknown
ENV WINDOW_SIZE=48
ENV WORKLOAD_REPEAT=18
ENV INNER_ITERS=260000

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "6000"]