FROM python:3.11-slim

WORKDIR /app

# 1. Install system dependencies (e.g., gcc)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
 && rm -rf /var/lib/apt/lists/*

# 2. Copy dependency files (requirements.txt)
COPY requirements.txt ./

# 3. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy application code
COPY src/ ./src/

ENV PYTHONUNBUFFERED=1

CMD ["python", "src/main.py"]
