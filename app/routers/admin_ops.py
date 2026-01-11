import os
import re
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db
from app.core.logger import logger

router = APIRouter(prefix="/admin/ops", tags=["Admin Operations"])

# Default backup name
BACKUP_SCHEMA = "schema_backup"

def validate_schema_name(name: str):
    """
    Security Check: Ensure schema name contains only alphanumeric chars and underscores.
    This prevents SQL Injection since schema names cannot be bound parameters in DDL.
    """
    if not re.match(r"^[a-zA-Z0-9_]+$", name):
        raise HTTPException(
            status_code=400, 
            detail="Invalid schema name. Only alphanumeric characters and underscores are allowed."
        )

@router.post("/init-staging", summary="Step 1: Create Staging Schema")
def init_staging_environment(
    schema_name: str = Query(..., description="Name of the staging schema to create"),
    db: Session = Depends(get_db)
):
    """
    1. Validates the schema name.
    2. Drops the schema if it exists (cleanup).
    3. Creates the new schema.
    4. Executes app/database/schema.sql inside that schema context.
    """
    # 1. Validation
    validate_schema_name(schema_name)
    
    sql_file_path = "app/database/schema.sql"
    if not os.path.exists(sql_file_path):
        logger.error(f"SQL file not found at: {sql_file_path}")
        raise HTTPException(status_code=500, detail="schema.sql file not found on server.")

    try:
        logger.info(f"🚀 Initializing staging schema: {schema_name}")

        with open(sql_file_path, "r") as f:
            sql_script = f.read()

        # Start Transaction
        with db.begin():
            # 2. Clean slate: Drop if exists
            db.execute(text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;"))
            
            # 3. Create Schema
            db.execute(text(f"CREATE SCHEMA {schema_name};"))
            
            # 4. Set Search Path
            # This is the magic trick. It forces the following CREATE TABLE statements
            # to run inside our new schema instead of 'public'.
            db.execute(text(f"SET search_path TO {schema_name};"))
            
            # 5. Execute Schema Definition
            db.execute(text(sql_script))
            
            # 6. Reset Search Path (Safety measure)
            db.execute(text("SET search_path TO public;"))
            
        logger.info(f"✅ Schema '{schema_name}' initialized successfully.")
        return {
            "status": "success", 
            "message": f"Schema '{schema_name}' created and tables initialized."
        }

    except Exception as e:
        logger.error(f"Init Failed: {e}")
        # Attempt cleanup if it fails halfway
        try:
            with db.begin():
                db.execute(text(f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;"))
        except:
            pass
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/swap-live", summary="Step 3: Make Staging Live")
def swap_schemas_live(
    staging_schema: str = Query(..., description="The staging schema to promote to public"),
    db: Session = Depends(get_db)
):
    """
    Atomic Blue/Green Deployment:
    1. Validates schema names.
    2. Checks if staging has data (sanity check).
    3. Renames 'public' -> 'schema_backup'.
    4. Renames 'staging_schema' -> 'public'.
    """
    validate_schema_name(staging_schema)

    try:
        logger.info(f"🔄 Initiating Schema Swap: {staging_schema} -> public")

        with db.begin():
            # 1. Sanity Check: Ensure staging actually has the core table
            # We use text() to safely construct the query, but variables are interpolated due to DDL restrictions
            check_query = text(f"SELECT to_regclass('{staging_schema}.occupations')")
            table_exists = db.execute(check_query).scalar()
            
            if not table_exists:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Staging schema '{staging_schema}' appears incomplete or missing tables."
                )

            # 2. Drop old backup if it exists (we only keep one previous version)
            db.execute(text(f"DROP SCHEMA IF EXISTS {BACKUP_SCHEMA} CASCADE;"))
            
            # 3. The Atomic Swap
            # A. Move live to backup
            db.execute(text(f"ALTER SCHEMA public RENAME TO {BACKUP_SCHEMA};"))
            
            # B. Move staging to live
            db.execute(text(f"ALTER SCHEMA {staging_schema} RENAME TO public;"))
            
        logger.info("✨ SUCCESS: Swap complete. New data is live.")
        return {
            "status": "success", 
            "message": f"Staging '{staging_schema}' is now LIVE. Old data backed up to '{BACKUP_SCHEMA}'."
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Swap Failed: {e}")
        raise HTTPException(status_code=500, detail=f"Database Swap Failed: {str(e)}")