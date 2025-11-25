FROM node:current-slim
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

# Switch to node user before npm ci to ensure correct ownership
USER node
RUN npm ci

# Copy source code
COPY --chown=node:node . /app/

EXPOSE 5173

# Run different commands based on NODE_ENV
CMD sh -c "\
if [ \"\$NODE_ENV\" = \"production\" ]; then \
    npm run build && npm run preview -- --host; \
else \
    npm run dev -- --host; \
fi\
"