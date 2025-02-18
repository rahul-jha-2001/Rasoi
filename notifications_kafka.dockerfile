FROM python:3.11-slim

# Combine RUN commands to reduce layers and optimize cache
RUN apt-get update && \
    apt-get install -y supervisor postgresql-client && \
    mkdir -p /etc/supervisor/conf.d && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files after installing dependencies
COPY ./Notifications .
COPY ./Notifications/kafka_entrypoint.sh /usr/local/bin/entrypoint.sh
COPY ./Notifications/kafka_supervisord.conf /etc/supervisor/conf.d/supervisord.conf

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH="${PYTHONPATH}:./proto"

RUN chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
