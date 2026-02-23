FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies (including dev dependencies for build)
RUN npm ci

# Copy source code
COPY frontend/ ./

# Copy nginx config into builder so final stage does not depend on build context
COPY docker/frontend/nginx.conf /tmp/nginx.conf

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration (from builder; build context must be repo root)
COPY --from=builder /tmp/nginx.conf /etc/nginx/nginx.conf

# Expose port 3000 (non-privileged)
EXPOSE 3000

# Start nginx
CMD ["nginx", "-g", "daemon off;"]