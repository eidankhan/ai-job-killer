# /app/core/logger.py
import os
import logging
from logging.handlers import RotatingFileHandler

# ---------------------------
# Determine project root
# ---------------------------
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

# Logs directory in project root
logs_dir = os.path.join(project_root, "logs")
os.makedirs(logs_dir, exist_ok=True)  # Ensure directory exists

# Log file path
log_file_path = os.path.join(logs_dir, "api.log")

# ---------------------------
# Create logger
# ---------------------------
logger = logging.getLogger("yt_transcript_api")
logger.setLevel(logging.INFO)

# Formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(formatter)

# File handler with rotation
file_handler = RotatingFileHandler(
    log_file_path, maxBytes=5*1024*1024, backupCount=5, encoding="utf-8"
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)

# Attach handlers only once
if not logger.hasHandlers():
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

logger.info(f"Logger initialized. Log file: {log_file_path}")
