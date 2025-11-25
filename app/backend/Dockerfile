# Builder stage for development - installs all dependencies including dev
FROM python:alpine AS builder-dev
LABEL maintainer="Jack Hannaway & Daniel O'Doherty"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install runtime libs, build deps, UV, and Python dependencies (with dev)
RUN set -eux; \
    apk add --no-cache --virtual .runtime-deps \
    # Runtime Libraries
    postgresql-libs jpeg zlib libpng tiff freetype lcms2 libwebp openjpeg; \
    apk add --no-cache --virtual .build-deps \
    # Build dependencies (removed later)
    gcc musl-dev postgresql-dev jpeg-dev zlib-dev libpng-dev tiff-dev freetype-dev lcms2-dev libwebp-dev openjpeg-dev curl; \
    # Install UV as standalone binary
    curl -LsSf https://astral.sh/uv/install.sh | sh; \
    export PATH="/root/.local/bin:$PATH"; \
    # Create venv in /opt/venv
    mkdir -p /opt; \
    uv venv /opt/venv; \
    # Install Python dependencies with dev extras
    uv pip install --python /opt/venv/bin/python -e ".[dev]"; \
    # Remove build deps (including curl) and clean up
    apk del .build-deps; \
    rm -rf /root/.cache /tmp/*

# Builder stage for production - installs only production dependencies
FROM python:alpine AS builder-prod
LABEL maintainer="Jack Hannaway & Daniel O'Doherty"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy dependency files first for better layer caching
COPY pyproject.toml uv.lock ./

# Install runtime libs, build deps, UV, and Python dependencies (production only)
RUN set -eux; \
    apk add --no-cache --virtual .runtime-deps \
    # Runtime Libraries
    postgresql-libs jpeg zlib libpng tiff freetype lcms2 libwebp openjpeg; \
    apk add --no-cache --virtual .build-deps \
    # Build dependencies (removed later)
    gcc musl-dev postgresql-dev jpeg-dev zlib-dev libpng-dev tiff-dev freetype-dev lcms2-dev libwebp-dev openjpeg-dev curl; \
    # Install UV as standalone binary
    curl -LsSf https://astral.sh/uv/install.sh | sh; \
    export PATH="/root/.local/bin:$PATH"; \
    # Create venv in /opt/venv
    mkdir -p /opt; \
    uv venv /opt/venv; \
    # Install Python dependencies (production only)
    uv pip install --python /opt/venv/bin/python .; \
    # Remove build deps (including curl) and clean up
    apk del .build-deps; \
    rm -rf /root/.cache /tmp/*

# Production stage - minimal runtime image
FROM python:alpine AS production
LABEL maintainer="Jack Hannaway & Daniel O'Doherty"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    COVERAGE_FILE=/tmp/.coverage \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Create user and directories
RUN set -eux; \
    adduser -D -s /bin/false -u 1000 django-user; \
    mkdir -p /vol/web/media /vol/web/static; \
    chmod -R 755 /vol; \
    chmod 1777 /tmp

# Install only runtime libraries (no build tools)
RUN apk add --no-cache \
    postgresql-libs jpeg zlib libpng tiff freetype lcms2 libwebp openjpeg

# Copy venv from production builder stage
COPY --from=builder-prod /opt/venv /opt/venv

# Copy source code
COPY --chown=django-user:django-user . /app/

# Ensure ownership
RUN chown -R django-user:django-user /app /vol /opt/venv

# Switch to non-root user
USER django-user

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# Development stage - includes dev dependencies and source
FROM python:alpine AS development
LABEL maintainer="Jack Hannaway & Daniel O'Doherty"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    COVERAGE_FILE=/tmp/.coverage \
    PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Create user and directories
RUN set -eux; \
    adduser -D -s /bin/false -u 1000 django-user; \
    mkdir -p /vol/web/media /vol/web/static; \
    chmod -R 755 /vol; \
    chmod 1777 /tmp; \
    chown -R django-user:django-user /app

# Install only runtime libraries (no build tools)
RUN apk add --no-cache \
    postgresql-libs jpeg zlib libpng tiff freetype lcms2 libwebp openjpeg

# Copy venv from development builder stage (includes dev dependencies)
COPY --from=builder-dev /opt/venv /opt/venv

# Copy source code
COPY --chown=django-user:django-user . /app/

# Ensure ownership
RUN chown -R django-user:django-user /app /vol /opt/venv

# Switch to non-root user
USER django-user

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
