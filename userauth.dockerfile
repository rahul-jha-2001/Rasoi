FROM python:3.13.3-slim

# Combine RUN commands to reduce layers and optimize cache
RUN apt-get update && \
    apt-get install -y supervisor postgresql-client && \
    mkdir -p /etc/supervisor/conf.d && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create a non-root user and set ownership
RUN groupadd -r appgroup && useradd -r -g appgroup appuser


WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY ./UserAuth/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files after installing dependencies
COPY ./UserAuth .
COPY ./Proto /app/Proto
COPY ./UserAuth/entrypoint.sh /usr/local/bin/entrypoint.sh
COPY ./UserAuth/grpc_supervisord.conf /etc/supervisor/conf.d/supervisord.conf
# ENV PYTHONUNBUFFERED=1 \
#     PYTHONPATH="${PYTHONPATH}:./proto"

RUN chmod +x /usr/local/bin/entrypoint.sh

# Change ownership of application files to non-root user
RUN chown -R appuser:appgroup /app /usr/local/bin/entrypoint.sh /etc/supervisor


# Switch to non-root user
USER appuser
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]