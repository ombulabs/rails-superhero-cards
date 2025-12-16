release: alembic upgrade head
web: uvicorn backend.main:app --host 0.0.0.0 --port $PORT
worker: celery -A backend.celery_worker worker --concurrency=2 --loglevel=info
