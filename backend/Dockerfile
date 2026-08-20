FROM python:3.11-slim as builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir --no-warn-script-location -r requirements.txt

FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

COPY . .
RUN mkdir -p /app/storage/videos

EXPOSE 8000
