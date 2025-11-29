#################### Base Stage ####################
FROM python:alpine AS base
LABEL maintainer="Jack Hannaway & Daniel O'Doherty"
LABEL description="Base image for the backend service of the Store Front project"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    COVERAGE_FILE=/tmp/.coverage \
    PATH="/root/.local/bin:/opt/venv/bin:$PATH" \
    VIRTUAL_ENV="/opt/venv"

WORKDIR /app

# Create user and directories (must run as root)
RUN set -eux; \
    adduser -D -s /bin/false -u 1000 django; \
    mkdir -p /vol/web/media /vol/web/static; \
    chmod -R 755 /vol; \
    chmod 1777 /tmp; \
    chown -R django:django /app;

# Copy dependency files first for better layer caching
COPY --chown=django:django pyproject.toml uv.lock ./

# Install all system dependencies (runtime + build dependencies) and UV
RUN set -eux; \
    apk add --no-cache \
    # Runtime libraries
    postgresql-libs jpeg zlib libpng tiff freetype lcms2 libwebp openjpeg \
    # Build dependencies (will be removed in final stages)
    --virtual .build-deps \
    gcc musl-dev postgresql-dev jpeg-dev zlib-dev libpng-dev tiff-dev freetype-dev lcms2-dev libwebp-dev openjpeg-dev curl; \
    curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mkdir -p /opt; \
    uv venv /opt/venv;

#################### Production stage ####################
FROM base AS production
RUN set -eux; \
    uv pip install .; \
    apk del .build-deps; \
    rm -rf /root/.cache /tmp/*; \
    chown -R django:django /vol /opt/venv

COPY --chown=django:django . /app/
USER django
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

#################### Development stage ####################
FROM base AS development
RUN set -eux; \
    uv pip install -e ".[dev]"; \
    apk del .build-deps; \
    rm -rf /root/.cache /tmp/*; \
    chown -R django:django /vol /opt/venv

COPY --chown=django:django . /app/
USER django
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
