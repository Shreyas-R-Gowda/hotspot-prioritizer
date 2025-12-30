FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for Pillow/Torch (libgl1 for cv2 if needed, though we use PIL. kept for safety)
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install CPU version of torch specifically to keep image light
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
