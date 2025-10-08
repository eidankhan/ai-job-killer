# app/api/routes/scoring_routes.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.services.scoring_service import ScoringService
from app.core.database import get_db  # Async DB session dependency

router = APIRouter(prefix="/scoring", tags=["Scoring"])

# -----------------------------
# Single occupation score
# -----------------------------
@router.get("/{occupation_id}")
async def get_occupation_score(
    occupation_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Fetch AI Job Risk Score for a single occupation by ID.
    """
    service = ScoringService(db)
    try:
        score_data = await service.get_occupation_score(occupation_id)
        return score_data
    except ValueError as ve:
        raise HTTPException(status_code=404, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to compute score")


# -----------------------------
# Bulk occupations score
# -----------------------------
@router.post("/bulk")
async def get_bulk_scores(
    occupation_ids: List[int] = Query(..., description="List of occupation IDs"),
    db: AsyncSession = Depends(get_db)
):
    """
    Compute AI Job Risk Scores for multiple occupations.
    """
    service = ScoringService(db)
    results = await service.bulk_score(occupation_ids)
    return {"count": len(results), "results": results}
