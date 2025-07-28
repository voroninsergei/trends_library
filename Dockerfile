# Use official Python runtime as a parent image
FROM python:3.12-slim

# Set work directory
WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project code
COPY . .

# Expose port 8000
EXPOSE 8000

# Ensure stdout and stderr are unbuffered
ENV PYTHONUNBUFFERED=1

# Command to run the FastAPI app
CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "8000"]
