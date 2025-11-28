# Stage 1: Build Stage - Uses Python 3.11
FROM python:3.11-slim as builder

# Set the working directory inside the container
WORKDIR /app

# Install ONLY the necessary system dependencies for compilation (build-essential, git).
# We REMOVE 'python3-dev' to prevent installing Python 3.13 headers.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        g++ \
        git \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
# Pip will use the Python 3.11 interpreter from the base image, 
# and the previously installed build tools will handle Pandas compilation.
RUN pip install --no-cache-dir -r requirements.txt

# ---
# Stage 2: Final Runtime Stage - Uses a clean, smaller base image
FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Copy only the installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy the application source code
COPY . .

# Expose the default port for Uvicorn
EXPOSE 8000

# Command to run the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
