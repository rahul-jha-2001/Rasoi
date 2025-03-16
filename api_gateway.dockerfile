# Stage 1: Builder for code generation
FROM golang:1.24 AS builder
ENV CGO_ENABLED=0
# Install system dependencies
RUN apt-get update && apt-get install -y \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./grpc_gateway/ .
COPY ./Proto ./Proto 
COPY ./grpc_gateway/builder.sh /usr/local/bin/builder.sh
RUN chmod +x /usr/local/bin/builder.sh
RUN  /usr/local/bin/builder.sh



# Command to run Supervisor

FROM alpine:latest
WORKDIR /app

# Install Supervisor
RUN apk add --no-cache supervisor

# Copy the compiled server binary
COPY ./grpc_gateway/gate_supervisord.conf /etc/supervisord.conf
COPY --from=builder ./app/server .

CMD ["supervisord", "-c", "/etc/supervisord.conf"]

# Copy the Supervisor configuration file
