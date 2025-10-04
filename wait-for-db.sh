#!/bin/sh
set -e

echo "Waiting for database at $DB_HOST:$DB_PORT..."

until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$POSTGRES_USER" > /dev/null 2>&1; do
  sleep 2
done

echo "Database is ready! Starting API..."
exec "$@"
