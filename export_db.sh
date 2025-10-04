#!/bin/bash

# =========================
# Configurable variables
# =========================
DB_USER=${POSTGRES_USER:-postgres}
DB_PASSWORD=${POSTGRES_PASSWORD:-postgres}
DB_NAME=${POSTGRES_DB:-fastapi_db}
DB_HOST=${POSTGRES_HOST:-localhost}
DB_PORT=${POSTGRES_PORT:-5432}
DUMP_FILE="db_dump.sql"

log() { echo "[INFO] $1"; }
error() { echo "[ERROR] $1"; }

# =========================
# Export DB using Docker
# =========================
export_db() {
    log "Exporting database '$DB_NAME' from $DB_HOST:$DB_PORT as user '$DB_USER'..."

    # Check if dump file already exists
    if [ -e "$DUMP_FILE" ]; then
        if [ -d "$DUMP_FILE" ]; then
            log "'$DUMP_FILE' is a directory. Removing it..."
            rm -rf "$DUMP_FILE"
        else
            log "'$DUMP_FILE' already exists. Overwriting..."
            rm -f "$DUMP_FILE"
        fi
    fi

    # Run pg_dump in a Docker container
    if docker run --rm \
        --network host \
        -e PGPASSWORD="$DB_PASSWORD" \
        postgres:15-alpine \
        pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$DB_NAME" > "$DUMP_FILE"
    then
        log "Database exported successfully to '$DUMP_FILE'."
    else
        error "Failed to export database."
        exit 1
    fi
}

# =========================
# Parse flags
# =========================
if [ "$1" == "all" ]; then
    export_db
else
    echo "Usage: $0 all"
    exit 1
fi
