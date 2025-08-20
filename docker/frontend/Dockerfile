FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy package files
COPY frontend/package*.json ./

# Install dependencies (including dev dependencies)
RUN npm install

# Copy source code
COPY frontend/ ./

# Expose port
EXPOSE 80

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "80"]