from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Any, Dict, List, Optional
from app.core.logger import logger
from app.core.database import get_db
from app.scoring.service import SimpleDbDrivenScorer, search_occupations
from app.core.deps import get_current_user, get_rate_limiter


router = APIRouter(prefix="/scoring", tags=["Scoring"])
scorer = SimpleDbDrivenScorer()


@router.get("/occupation", response_model=Dict[str, Any])
def get_score_by_occupation_name(
    name: str = Query(..., description="Name or label of the occupation (fuzzy search)"),
    db: Session = Depends(get_db)
    # _limit: bool = Depends(get_rate_limiter) # <-- This handles everything!
):
    """
    Compute and return a vulnerability score for an occupation based on its name.
    Example:
        GET /scoring/occupation?name=Software%20Developer
    """
    logger.info(f"Request received: score_by_occupation_name name='{name}'")
    try:
        result = scorer.score_by_occupation_name(db, name)
        logger.info(f"Successfully computed score for occupation name='{name}'")
        return result
    except ValueError as e:
        logger.warning(f"Occupation not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error occurred while scoring occupation name='{name}': {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/occupation/{occupation_id}", response_model=Dict[str, Any])
def get_score_by_occupation_id(
    occupation_id: int,
    db: Session = Depends(get_db),
    _limit: bool = Depends(get_rate_limiter) # <-- This handles everything!
):
    """
    Compute and return a vulnerability score for a given occupation_id.
    Example:
        GET /scoring/occupation/123
    """
    logger.info(f"Request received: score_by_occupation_id id={occupation_id}")
    try:
        result = scorer.score_by_occupation_id(db, occupation_id)
        logger.info(f"Successfully computed score for occupation_id={occupation_id}")
        return result
    except ValueError as e:
        logger.warning(f"Occupation ID not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error occurred while scoring occupation_id={occupation_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


@router.get("/buckets", response_model=Dict[str, Any])
def get_bucket_keywords(
    db: Session = Depends(get_db),
):
    """
    Return all bucket keywords and their metadata.
    Useful for inspecting what keyword triggers what scoring bucket.
    Example:
        GET /scoring/buckets
    """
    logger.info("Request received: get_bucket_keywords")
    try:
        buckets = scorer._load_bucket_keywords(db)
        logger.info(f"Successfully retrieved {len(buckets)} buckets")
        return {"count": len(buckets), "buckets": buckets}
    except Exception as e:
        logger.error(f"Unexpected error occurred while loading bucket keywords: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
@router.get("/search", response_model=List[Dict[str, str]])
def search_occupations_endpoint(
    query: str = Query(..., min_length=1),
    db: Session = Depends(get_db)
    # user: Optional[Dict] = Depends(get_current_user) # <-- Still good to have
):
    """
    API endpoint to search occupations for autocomplete.
    """
    results = search_occupations(db, query)
    return results

