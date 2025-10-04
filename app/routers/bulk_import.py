from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.bulk_import_service import BulkImportService

router = APIRouter(prefix="/bulk-import", tags=["Bulk Import"])

@router.post("/load-all")
def load_all_data(db: Session = Depends(get_db)):
    """
    Load and import all five CSV files into the database sequentially.
    """
    try:
        result = BulkImportService.import_all(db)
        return {"status": "success", "inserted_counts": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error importing CSV files: {str(e)}")
