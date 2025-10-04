FROM python:3.11-slim

WORKDIR /app

# Install dependencies for PostgreSQL client and build tools if needed
RUN apt-get update && \
    apt-get install -y build-essential libffi-dev python3-dev postgresql-client && \
    rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY ./app ./app

# Ensure logging config is copied into the image
COPY ./app/core/logging_config.yaml ./app/core/logging_config.yaml

# Copy DB import script
COPY ./import_db.sh /app/import_db.sh
RUN chmod +x /app/import_db.sh

# Optional: copy a DB dump if you want it baked into the image
# COPY ./db_dump.sql /app/db_dump.sql

EXPOSE 8000

ENTRYPOINT ["/app/import_db.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--log-config", "app/core/logging_config.yaml", "--access-log", "/app/logs/access.log"]
