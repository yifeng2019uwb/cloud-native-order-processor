# Use the official AWS Lambda Python base image (or a standard Python image for a web server)
FROM public.ecr.aws/lambda/python:3.11 # Or python:3.11-slim-buster for a web server

WORKDIR /var/task # Or /app for a web server

COPY requirements.txt .
RUN pip install -r requirements.txt --target . --no-cache-dir

COPY . .

# If it's a web server (e.g., Flask/Django), you might expose a port and use a WSGI server
# EXPOSE 8000
# CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app:app"] # Example for Flask

# If it's a Lambda function, keep the CMD as before:
CMD [ "app.lambda_handler" ]