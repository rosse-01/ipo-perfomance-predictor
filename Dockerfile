# 1. Official slim Python base image
FROM python:3.11-slim

# 2. Prevent Python from writing .pyc files and buffer streams
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 3. Install lightweight build essentials for NumPy / Scikit-Learn compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy the lean requirements file first
COPY requirements.txt .

# 5. Upgrade pip and install core production dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 6. Copy your API files and .pkl binaries into the container
COPY main.py .
COPY best_rf_model.pkl .
COPY scaler.pkl .

# 7. Expose the standard web server port
EXPOSE 8000

# 8. Start the Uvicorn production server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]