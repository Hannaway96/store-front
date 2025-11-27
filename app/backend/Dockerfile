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

# Install all system dependencies (runtime + build dependencies) and UV
ENV PATH="/root/.local/bin:$PATH"
RUN set -eux; \
    apk add --no-cache \
    # Runtime libraries
    postgresql-libs jpeg zlib libpng tiff freetype lcms2 libwebp openjpeg \
    # Build dependencies (will be removed in final stages)
    --virtual .build-deps \
    gcc musl-dev postgresql-dev jpeg-dev zlib-dev libpng-dev tiff-dev freetype-dev lcms2-dev libwebp-dev openjpeg-dev curl; \
    curl -LsSf https://astral.sh/uv/install.sh | sh

#################### install dependencies stage ####################
FROM base AS install-dependencies
# Install Python dependencies (with dev)
RUN set -eux; \
    mkdir -p /opt; \
    uv venv /opt/venv; \
    uv pip install --python /opt/venv/bin/python -e ".[dev]"; \
    apk del .build-deps; \
    rm -rf /root/.cache /tmp/*

#################### Prod Build stage ####################
FROM base AS builder
# Install Python dependencies (production only)
RUN set -eux; \
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

# Remove build dependencies (not needed at runtime)
RUN apk del .build-deps && \
    chown -R django-user:django-user /app /vol /opt/venv

# Switch to non-root user
USER django-user
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

#################### Development stage ####################
FROM base AS development
COPY --from=install-dependencies --chown=django-user:django-user /opt/venv /opt/venv
COPY --chown=django-user:django-user . /app/

# Remove build dependencies (not needed at runtime)
RUN apk del .build-deps && \
    chown -R django-user:django-user /app /vol /opt/venv

# Switch to non-root user
USER django-user
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
