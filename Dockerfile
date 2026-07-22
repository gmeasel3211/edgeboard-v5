FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /code

COPY apps/api/pyproject.toml /code/pyproject.toml
COPY apps/api/app /code/app
RUN pip install --upgrade pip && pip install .

COPY apps/api/alembic.ini /code/alembic.ini
COPY apps/api/alembic /code/alembic

EXPOSE 8000
CMD ["fastapi", "run", "app/main.py", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
