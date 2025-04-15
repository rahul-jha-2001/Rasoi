#!/bin/bash
set -e  # Exit on error
set -o pipefail

echo "Entrypoint started..."

# === CONFIG ===
MAX_RETRIES=3
SLEEP_TIME=2
LOCK_FILE="/tmp/db_created.lock"
LOG_FILE="/app/logs/db-init.log"

# === REQUIRED VARS CHECK ===
required_vars=("POSTGRES_HOST" "POSTGRES_USER" "POSTGRES_PASSWORD" "POSTGRES_DB")
for var in "${required_vars[@]}"; do
  if [ -z "${!var}" ]; then
    echo "❌ ERROR: $var is not set. Exiting." | tee -a "$LOG_FILE"
    exit 1
  fi
done

echo "Environment variables loaded." | tee -a "$LOG_FILE"
echo $POSTGRES_HOST
# === SKIP IF ALREADY CREATED ===
if [ -f "$LOCK_FILE" ]; then
  echo " Database already initialized. Skipping creation." | tee -a "$LOG_FILE"
else
  echo " Waiting for PostgreSQL (RDS) to be ready..." | tee -a "$LOG_FILE"
  RETRY_COUNT=0
  until PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d postgres -c '\q' 2>/dev/null; do
    echo " PostgreSQL is unavailable - retrying in $SLEEP_TIME sec" | tee -a "$LOG_FILE"
    RETRY_COUNT=$((RETRY_COUNT+1))
    if [ $RETRY_COUNT -ge $MAX_RETRIES ]; then
      echo " ERROR: PostgreSQL did not become available in time" | tee -a "$LOG_FILE"
      exit 1
    fi

    sleep $SLEEP_TIME
    SLEEP_TIME=$((SLEEP_TIME * 2))  # exponential backoff
  done

  echo " PostgreSQL is up!" | tee -a "$LOG_FILE"

  # === CHECK & CREATE DATABASE IF NEEDED ===
  echo " Checking if database '${POSTGRES_DB}' exists..." | tee -a "$LOG_FILE"
  if ! PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d postgres -tc \
    "SELECT 1 FROM pg_database WHERE datname = '${POSTGRES_DB}';" | grep -q 1; then
    echo " Creating database '${POSTGRES_DB}'..." | tee -a "$LOG_FILE"
    if ! PGPASSWORD=$POSTGRES_PASSWORD psql -h $POSTGRES_HOST -U $POSTGRES_USER -d postgres -c "CREATE DATABASE ${POSTGRES_DB};"; then
      echo " ERROR: Failed to create database '${POSTGRES_DB}'" | tee -a "$LOG_FILE"
      exit 1
    fi
    echo " Database '${POSTGRES_DB}' created successfully." | tee -a "$LOG_FILE"
  else
    echo " Database '${POSTGRES_DB}' already exists." | tee -a "$LOG_FILE"
  fi

  touch "$LOCK_FILE"
fi

echo "Entering proto folder..."
cd Proto || { echo "Error: proto directory not found!"; exit 1; }
echo "Compiling Proto Files..."

if ! python -m grpc_tools.protoc  -I=.  --python_out=. --grpc_python_out=. --pyi_out=. *.proto; then
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

echo "Starting GRPC..."

exec supervisord -c /etc/supervisor/conf.d/supervisord.conf