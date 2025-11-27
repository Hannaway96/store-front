#################### Base Stage ####################
FROM python:alpine AS base
LABEL maintainer="Jack Hannaway & Daniel O'Doherty"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    COVERAGE_FILE=/tmp/.coverage \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Create user and directories (must run as root)
RUN set -eux; \
    adduser -D -s /bin/false -u 1000 django-user; \
    mkdir -p /vol/web/media /vol/web/static; \
    chmod -R 755 /vol; \
    chmod 1777 /tmp; \
    chown -R django-user:django-user /app

# Copy dependency files first for better layer caching
COPY --chown=django-user:django-user pyproject.toml uv.lock ./
# Install runtime libraries (needed for both build and runtime)
RUN apk add --no-cache \
    postgresql-libs jpeg zlib libpng tiff freetype lcms2 libwebp openjpeg

#################### install dependencies stage ####################
FROM base AS install-dependencies
# Install build dependencies, UV, and Python dependencies (with dev)
RUN set -eux; \
    apk add --no-cache --virtual .build-deps \
    gcc musl-dev postgresql-dev jpeg-dev zlib-dev libpng-dev tiff-dev freetype-dev lcms2-dev libwebp-dev openjpeg-dev curl; \
    curl -LsSf https://astral.sh/uv/install.sh | sh; \
    export PATH="/root/.local/bin:$PATH"; \
    mkdir -p /opt; \
    uv venv /opt/venv; \
    uv pip install --python /opt/venv/bin/python -e ".[dev]"; \
    apk del .build-deps; \
    rm -rf /root/.cache /tmp/*

#################### Prod Build stage ####################
FROM base AS builder
# Install build dependencies, UV, and Python dependencies (production only)
RUN set -eux; \
    apk add --no-cache --virtual .build-deps \
    gcc musl-dev postgresql-dev jpeg-dev zlib-dev libpng-dev tiff-dev freetype-dev lcms2-dev libwebp-dev openjpeg-dev curl; \
    curl -LsSf https://astral.sh/uv/install.sh | sh; \
    export PATH="/root/.local/bin:$PATH"; \
    mkdir -p /opt; \
    uv venv /opt/venv; \
    uv pip install --python /opt/venv/bin/python .; \
    apk del .build-deps; \
    rm -rf /root/.cache /tmp/*

# Copy source code
COPY --chown=django-user:django-user . /app/

#################### Production stage ####################
FROM base AS production
COPY --from=builder --chown=django-user:django-user /opt/venv /opt/venv
COPY --chown=django-user:django-user . /app/

RUN chown -R django-user:django-user /app /vol /opt/venv

# Switch to non-root user
USER django-user
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

#################### Development stage ####################
FROM base AS development
COPY --from=install-dependencies --chown=django-user:django-user /opt/venv /opt/venv
COPY --chown=django-user:django-user . /app/

# Ensure ownership
RUN chown -R django-user:django-user /app /vol /opt/venv

# Switch to non-root user
USER django-user
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
