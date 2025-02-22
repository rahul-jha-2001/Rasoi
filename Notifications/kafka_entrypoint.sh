#!/bin/bash
set -e

# Add timeout to prevent infinite waiting
MAX_RETRIES=30
RETRY_COUNT=0

echo "Waiting for PostgreSQL to be ready..."
echo "POSTGRES_PASSWORD: $POSTGRES_PASSWORD"
echo "POSTGRES_HOST: $POSTGRES_HOST"
echo "POSTGRES_USER: $POSTGRES_USER"
echo "POSTGRES_DB: $POSTGRES_DB"

until PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -c '\q' 2>/dev/null; do
    echo "PostgreSQL is unavailable - sleeping"
    RETRY_COUNT=$((RETRY_COUNT+1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
        echo "Error: PostgreSQL did not become available in time"
        exit 1
    fi
    sleep 1
done
echo "PostgreSQL is up and running!"

# Add error handling for database creation
echo "Checking if database ${SERVICE_NAME}_db exists..."
if ! PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -tc \
    "SELECT 1 FROM pg_database WHERE datname = '${SERVICE_NAME}_db'" | grep -q 1; then
    echo "Creating database ${SERVICE_NAME}_db..."
    if ! PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -c "CREATE DATABASE ${SERVICE_NAME}_db"; then
        echo "Failed to create database"
        exit 1
    fi
    echo "Database created successfully"
fi

echo "Entering proto folder..."
cd proto || { echo "Error: proto directory not found!"; exit 1; }

echo "Compiling Proto Files..."
if ! python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. --pyi_out=. *.proto; then
    echo "Could Not Compile Proto Files"
    cd ..
    exit 1
fi

echo "Proto compilation successful!"
cd ..
echo "Returned to original directory"

# Add error handling for migrations
echo "Starting migrations..."
if ! python -m manage makemigrations; then
    echo "Failed to make migrations"
    exit 1
fi

if ! python -m manage migrate; then
    echo "Failed to apply migrations"
    exit 1
fi
echo "Migrations applied successfully"

echo "Starting Kafka consumer..."

exec supervisord -c /etc/supervisor/conf.d/supervisord.conf