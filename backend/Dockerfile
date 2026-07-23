FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_NO_DEV=1 \
    UV_PROJECT_ENVIRONMENT=/usr/local

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-install-project

COPY . .

ENV DJANGO_SETTINGS_MODULE=config.settings
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]