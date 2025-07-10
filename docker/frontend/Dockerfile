FROM nginx:alpine

# Copy simple HTML frontend
COPY frontend-simple/ /usr/share/nginx/html/

# Copy nginx config for API routing
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
