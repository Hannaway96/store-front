#################### Base Stage ####################
FROM node:alpine AS base
LABEL maintainer="Jack Hannaway & Daniel O'Doherty"
ENV NPM_CONFIG_UPDATE_NOTIFIER=false \
    NPM_CONFIG_FUND=false \
    NPM_CONFIG_AUDIT=false

WORKDIR /app
# Ensure /app is owned by node user (must run as root)
RUN chown -R node:node /app
# Copy package files first for better layer caching
COPY --chown=node:node package*.json ./
# Switch to node user
USER node

#################### Production stage ####################
FROM base AS production
RUN set -eux; \
    npm ci && \
    npm cache clean --force;

COPY --chown=node:node . /app/
RUN npm run build

RUN set -eux; \
    npm ci --omit=dev && \
    npm cache clean --force;    chown -R node:node /app
EXPOSE 5173
CMD ["npm", "run", "serve"]

#################### Development stage ####################
FROM base AS development
ENV NODE_ENV=development
RUN npm ci && npm cache clean --force
COPY --chown=node:node . /app/
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
