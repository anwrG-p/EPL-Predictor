# === Stage 1: Builder Stage ===
# Use a full Python image for installing packages that might require compilation (like numpy, scipy, xgboost)
FROM python:3.11-slim as builder

# Set the working directory inside the container
WORKDIR /app

# Install necessary system dependencies for package compilation
# This includes tools needed to build some Python wheels (e.g., NumPy, SciPy)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
# The log indicates this is the step that takes a long time and installs all packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---
# === Stage 2: Final Runtime Stage (Slim and Secure) ===
# Use a lean Python image for the final deployment to reduce image size
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy the core Python packages from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy the application source code
COPY . .

# CRITICAL FIX for "gunicorn executable file not found in $PATH":
# We must re-install the lightweight server packages in the final stage to ensure their
# executable scripts (which reside in /usr/local/bin) are correctly generated and visible
# in the final image's $PATH, preventing the Status 128 error.
RUN pip install --no-cache-dir uvicorn gunicorn

# --- Security and Permissions ---
# Create a non-root user (appuser) for security best practices
RUN adduser --disabled-password --gecos "" appuser
# Change ownership of the application directory to the new non-root user
RUN chown -R appuser:appuser /app
# Switch to the non-root user for all subsequent commands
USER appuser

# Expose the default port for Uvicorn/Gunicorn
EXPOSE 8000

# Set the environment variables for Uvicorn
ENV PYTHONUNBUFFERED=1

# Command to run the FastAPI application using Gunicorn and Uvicorn workers (production setup)
CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
