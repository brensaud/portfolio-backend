FROM python:3.12-slim

# Install uv — fast Python package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

# Set a writable UV cache directory inside the image
ENV UV_CACHE_DIR=/tmp/uv-cache

# Copy dependency manifests first (layer caching)
COPY pyproject.toml uv.lock ./

# Install production dependencies only (no dev extras)
RUN uv sync --frozen --no-dev

# Copy application source
COPY app/ ./app/
COPY alembic.ini ./
COPY alembic/ ./alembic/
COPY main.py ./

# Non-root user for security
RUN useradd --no-create-home --shell /bin/false appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# Run migrations then start the server
CMD ["sh", "-c", "uv run alembic upgrade head && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000"]
