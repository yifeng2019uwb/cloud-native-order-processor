# Remove the default Nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy your custom Nginx configuration
# Create a file named 'nginx.conf' in your frontend-html/ directory like this:
#
#   events { worker_connections 1024; }
#   http {
#       include       /etc/nginx/mime.types;
#       default_type  application/octet-stream;
#       server {
#           listen 80;
#           server_name localhost;
#           root /usr/share/nginx/html;
#           index index.html index.htm;
#           location / {
#               try_files $uri $uri/ =404;
#           }
#       }
#   }
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy your static HTML/CSS/JS files into the Nginx web root
COPY . /usr/share/nginx/html

# Expose port 80
EXPOSE 80

# Command to run Nginx (default for nginx:alpine)
CMD ["nginx", "-g", "daemon off;"]