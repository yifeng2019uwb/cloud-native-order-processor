FROM nginx:alpine

# Copy built frontend files
COPY ../../frontend/dist/ /usr/share/nginx/html/

# Copy nginx config for API routing
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
