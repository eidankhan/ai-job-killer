#!/bin/bash
set -euo pipefail

# import_db.sh
# - imports /app/db_dump.sql into the DB once (creates /app/.db_imported)
# - then starts the command passed as CMD (e.g. uvicorn ...)

LOGFILE="/app/manage.log"
DUMP_FILE="/app/db_dump.sql"
IMPORTED_FLAG="/app/.db_imported"

DB_USER="${POSTGRES_USER:-postgres}"
DB_NAME="${POSTGRES_DB:-fastapi_db}"
DB_HOST="${POSTGRES_HOST:-db}"
DB_PORT="${POSTGRES_PORT:-5432}"
DB_PASSWORD="${POSTGRES_PASSWORD:-}"

log() {
  echo "[INFO] $(date +'%Y-%m-%d %H:%M:%S') $*" | tee -a "$LOGFILE"
}

# Ensure log file exists
: > "$LOGFILE" 2>/dev/null || true

if [ -f "$DUMP_FILE" ] && [ ! -f "$IMPORTED_FLAG" ]; then
    log "Dump file '$DUMP_FILE' found. Preparing to import..."

    # Wait until database is ready (use PGPASSWORD for auth during check)
    log "Waiting for database at $DB_HOST:$DB_PORT to become ready..."
    until PGPASSWORD="$DB_PASSWORD" pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" >/dev/null 2>&1; do
        log "Waiting for database..."
        sleep 2
    done

    log "Database is ready. Starting import (password will not be echoed)..."

    # Import. If it fails we log the error but continue to start the server.
    if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$DUMP_FILE"; then
        log "Database import completed successfully."
    else
        log "Database import finished with errors (see psql output); continuing to start the app."
    fi

    # mark imported so we do not re-import on container restart
    touch "$IMPORTED_FLAG" || log "Warning: failed to create marker file $IMPORTED_FLAG"
elif [ -f "$IMPORTED_FLAG" ]; then
    log "Import marker found. Skipping DB import."
else
    log "No dump file found. Skipping DB import."
fi

# Start the main process (uvicorn or whatever is passed as CMD)
log "Starting main process: $*"
exec "$@"
