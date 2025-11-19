FROM node:22-slim
LABEL maintainers="Jack Hannaway & Daniel O Doherty"

ENV NODE_ENV=development \
    NPM_CONFIG_UPDATE_NOTIFIER=false \
    NPM_CONFIG_FUND=false \
    NPM_CONFIG_AUDIT=false

ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupmod -o -g ${GROUP_ID} node && usermod -o -u ${USER_ID} -g ${GROUP_ID} node
WORKDIR /app

# Make sure /app exists and is writable by "node"
RUN mkdir -p /app && chown -R node:node /app

# Copy package files first for better layer caching
COPY --chown=node:node package*.json ./
RUN [ -f package.json ] && npm ci || true

# Copy source code
COPY --chown=node:node . /app/

# Switch to the pre-created non-root user
USER node

EXPOSE 5173
CMD ["npm","run","dev","--","--host"]