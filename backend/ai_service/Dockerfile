FROM python:3.11-slim

WORKDIR /app
COPY ai_service /app/ai_service
COPY ai_core /app/ai_core
COPY ai_service/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

ENV PYTHONUNBUFFERED=1
ENV PORT=8080
CMD exec uvicorn ai_service.app:app --host 0.0.0.0 --port $PORT
