# Build from the repository root (the API imports the `backend` package):
#   docker build -f backend/Dockerfile .
FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY backend/requirements.txt backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend backend

# The trained model is not baked in: compose mounts models/artifacts read-only, so a
# retrained model is picked up without rebuilding the image.
ENV MODEL_PATH=/app/models/artifacts/churn_model.joblib

RUN useradd --system --uid 10001 api
USER api

EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
