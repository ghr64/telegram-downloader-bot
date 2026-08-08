# Multi-stage build: bgutil server + Python bot
# Stage 1: Get the bgutil HTTP server binary (using the prebuilt Docker image)
FROM brainicism/bgutil-ytdlp-pot-provider:latest AS pot-server

# Stage 2: Python bot with bgutil server
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy bgutil server from stage 1
COPY --from=pot-server /app /pot-server

# Set up working directory
WORKDIR /app

# Copy bot requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY bot.py .
COPY cookies.txt .

# Create supervisord config to run both services
RUN mkdir -p /etc/supervisor/conf.d

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Expose ports (bgutil server on 4416, bot doesn't need exposed port for polling)
EXPOSE 4416

# Run supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
