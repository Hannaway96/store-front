FROM node:alpine AS base
LABEL maintainer="Jack Hannaway & Daniel O'Doherty"

ARG NODE_ENV=production

ENV NODE_ENV=${NODE_ENV} \
    NPM_CONFIG_UPDATE_NOTIFIER=false \
    NPM_CONFIG_FUND=false \
    NPM_CONFIG_AUDIT=false

WORKDIR /app

# Ensure /app is owned by node user (must run as root)
RUN chown -R node:node /app

# Copy package files first for better layer caching
COPY --chown=node:node package*.json ./

# Install dependencies as node user
USER node
RUN npm ci && \
    npm cache clean --force

# Copy source code
COPY --chown=node:node . /app/

# Build stage - only builds in production
FROM base AS builder
RUN if [ "$NODE_ENV" = "production" ]; then \
    npm run build; \
    fi

# Production stage - minimal runtime image
FROM node:alpine AS production
LABEL maintainer="Jack Hannaway & Daniel O'Doherty"

ENV NODE_ENV=production \
    NPM_CONFIG_UPDATE_NOTIFIER=false \
    NPM_CONFIG_FUND=false \
    NPM_CONFIG_AUDIT=false

WORKDIR /app

# Ensure /app is owned by node user (must run as root)
RUN chown -R node:node /app

# Copy only built artifacts and production dependencies
COPY --from=builder --chown=node:node /app/dist ./dist
COPY --from=builder --chown=node:node /app/node_modules ./node_modules
COPY --from=builder --chown=node:node /app/package*.json ./

# Ensure ownership after copy
RUN chown -R node:node /app

USER node
EXPOSE 5173
CMD ["npm", "run", "preview", "--", "--host"]

# Development stage - includes dev dependencies and source
FROM base AS development
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
