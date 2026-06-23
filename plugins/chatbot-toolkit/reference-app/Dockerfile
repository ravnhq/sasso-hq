# Multi-stage build: install into a non-editable venv, then ship only the venv.
FROM python:3.12-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV UV_COMPILE_BYTECODE=1 \
    UV_PYTHON_DOWNLOADS=0
WORKDIR /app

# Install dependencies first (cached layer), without the project or dev group.
COPY uv.lock pyproject.toml ./
RUN uv sync --locked --no-install-project --no-dev --no-editable

# Then install the project itself into the venv.
COPY . /app
RUN uv sync --locked --no-dev --no-editable

FROM python:3.12-slim
# Run as a non-root user.
RUN useradd --create-home --uid 10001 app
COPY --from=builder --chown=app:app /app/.venv /app/.venv
USER app

ENV PATH="/app/.venv/bin:$PATH"
EXPOSE 8000
# PaaS platforms inject $PORT; fall back to 8000 locally.
CMD ["sh", "-c", "uvicorn app.main:create_default_app --factory --host 0.0.0.0 --port ${PORT:-8000}"]
