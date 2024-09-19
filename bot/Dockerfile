FROM python:3.11-slim

RUN apt-get update && \
    apt-get install -y redis-tools && \
    apt-get install -y redis-server && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /bot

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt    

COPY . .

CMD ["python", "__main__.py"]
