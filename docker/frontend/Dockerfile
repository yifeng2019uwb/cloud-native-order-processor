# Build stage
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies (not production-only to include dev dependencies for build)
RUN npm ci

# Copy source code (excluding node_modules)
COPY frontend/ ./

# Remove any existing node_modules to ensure clean build
RUN rm -rf node_modules

# Reinstall dependencies for the target platform
RUN npm ci

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built frontend files from build stage
COPY --from=build /app/dist/ /usr/share/nginx/html/

# Copy nginx config for API routing
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
