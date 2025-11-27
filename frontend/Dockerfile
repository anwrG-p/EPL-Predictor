FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for scipy/numpy compilation if needed
RUN apt-get update && apt-get install -y git build-essential

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Environment variable to ensure outputs are flushed
ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
