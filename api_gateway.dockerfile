# Stage 1: Builder for code generation
FROM golang:1.24 AS builder
ENV CGO_ENABLED=0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    protobuf-compiler \
    && rm -rf /var/lib/apt/lists/*

RUN go install github.com/grpc-ecosystem/grpc-gateway/v2/protoc-gen-grpc-gateway@latest
RUN go install github.com/grpc-ecosystem/grpc-gateway/v2/protoc-gen-openapiv2@latest
RUN go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
RUN go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

WORKDIR /app

# Copy application files
COPY ./grpc_gateway/ .
RUN go mod tidy

COPY ./Proto ./Proto 
COPY ./grpc_gateway/builder.sh /usr/local/bin/builder.sh
RUN chmod +x /usr/local/bin/builder.sh
RUN /usr/local/bin/builder.sh

# Stage 2: Runtime environment
FROM alpine:latest
WORKDIR /app

# Install Supervisor
RUN apk add --no-cache supervisor

# Copy the compiled server binary
COPY ./grpc_gateway/gate_supervisord.conf /etc/supervisord.conf
COPY ./grpc_gateway/rasoi-auth-firebase-adminsdk-fbsvc-2131b3731f.json .
COPY --from=builder /app/server .



RUN chmod +x server

CMD ["supervisord", "-c", "/etc/supervisord.conf"]
