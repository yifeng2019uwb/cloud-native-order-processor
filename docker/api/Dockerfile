# Use the desired stable Python 3.11 version for better compatibility
FROM python:3.11-slim-buster

# Set the working directory inside the container
WORKDIR /app

# --- Diagnostic Step: Check Python Version ---
# This command will print the Python version being used in this build stage.
RUN python --version

# Install system dependencies required for building Python packages.
# This includes:
# - build-essential: Provides compilers (gcc, g++) needed for many native extensions.
# - curl: To download the Rust installer script.
# - librdkafka-dev: Development headers for librdkafka, required by confluent-kafka.
# - libpq-dev: Development headers for PostgreSQL, required by psycopg2-binary.
# - pkg-config: Utility often needed by build systems to find installed libraries.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    librdkafka-dev \
    libpq-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for Rust and Cargo.
# These ensure Rust tools are installed to persistent locations within the image
# and are correctly added to the system's PATH.
ENV RUSTUP_HOME=/usr/local/rustup \
    CARGO_HOME=/usr/local/cargo \
    PATH=/usr/local/cargo/bin:$PATH

# Install Rust and Cargo using rustup.
# This entire operation is in a single RUN command to ensure environment changes are persistent.
# -sSf: Silent and fail-fast download.
# -y: Non-interactive installation.
# --profile minimal: Installs only essential Rust components to keep image size small.
# --no-modify-path: Prevents rustup from modifying shell profiles, as PATH is handled by ENV.
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --no-modify-path \
    # Ensure write permissions for Rust installation directories
    && chmod -R a+w "$RUSTUP_HOME" "$CARGO_HOME" \
    # Explicitly set the stable Rust toolchain
    && /usr/local/cargo/bin/rustup default stable

# Copy your requirements file into the container
COPY requirements.txt .

# Install Python dependencies.
# This step will now have access to a compatible Python version (3.11) and a fully installed Rust/Cargo toolchain.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code
COPY . .

# Define the command to run your application (adjust as needed for your specific entry point)
# Example:
CMD ["python", "your_app_entrypoint.py"]