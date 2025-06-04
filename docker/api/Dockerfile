# FROM python:3.9-slim

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY app.py .

# EXPOSE 5000

# CMD ["python", "app.py"]

# Use the official AWS Lambda Python base image
# This image is optimized for Lambda and includes the runtime interface client (RIC)
# Choose the Python version that matches your Lambda runtime (e.g., 3.9, 3.10, 3.11, 3.12)
FROM public.ecr.aws/lambda/python:3.11

# Set the working directory in the container
WORKDIR /var/task

# Copy the requirements.txt file into the container
# This step is cached, so dependencies are only reinstalled if requirements.txt changes
COPY requirements.txt .

# Install Python dependencies
# The --no-cache-dir flag is used to prevent pip from storing downloaded packages,
# which helps keep the image size small.
RUN pip install -r requirements.txt --target . --no-cache-dir

# Copy your Lambda function code into the container
# The '.' copies everything from the build context (the directory where Dockerfile is)
COPY . .

# Set the CMD to your handler (e.g., 'your_file_name.your_handler_function_name')
# For example, if your file is 'app.py' and your handler function is 'lambda_handler',
# then CMD would be 'app.lambda_handler'
CMD [ "app.lambda_handler" ]