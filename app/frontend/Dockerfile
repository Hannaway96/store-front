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

#################### install dependencies stage ####################
FROM base AS install-dependencies
# Install all dependencies  
RUN npm ci && npm cache clean --force

#################### Prod Build stage ####################
FROM base AS builder
COPY --from=install-dependencies --chown=node:node /app/node_modules ./node_modules
# Copy source code
COPY --chown=node:node . /app/
# Build the application
RUN npm run build

#################### Production stage ####################
FROM base AS production
ENV NODE_ENV=production
# Copy built application
COPY --from=builder --chown=node:node /app/dist ./dist
COPY --from=builder --chown=node:node /app/package*.json ./
# Install only production dependencies
RUN npm ci --omit=dev && npm cache clean --force
EXPOSE 5173
CMD ["npm", "run", "serve"]

#################### Development stage ####################
FROM base AS development
ENV NODE_ENV=development
# Copy all installed dependencies
COPY --from=install-dependencies --chown=node:node /app/node_modules ./node_modules
# Copy source code
COPY --chown=node:node . /app/
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host"]
