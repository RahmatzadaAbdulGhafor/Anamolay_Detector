FROM python:3.10

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /app/
WORKDIR /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app
EXPOSE 8050

CMD ["python", "app.py"]
