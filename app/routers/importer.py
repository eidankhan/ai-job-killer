# app/routers/importer.py
from app.services.data_importer import import_data
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
router = APIRouter()
    
@router.post("/data/import")
def import_data_endpoint(db: Session = Depends(get_db)):
    """
    Import cleaned CSVs into Postgres.
    """
    try:
        import_data(db)
        return JSONResponse(
            status_code=200,
            content={"Data Imported successfully"},
        )
    except:
        return JSONResponse(
            status_code=500,
            content={"Unable to import data"},
        )
