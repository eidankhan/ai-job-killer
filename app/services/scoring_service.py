# app/services/scoring_service.py
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.logger import logger

from app.db.scoring_repository import fetch_occupation_skills_for_scoring

class ScoringService:
    """
    Orchestrates fetching and computing occupation-level automation risk scores.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_occupation_score(self, occupation_id: int) -> Dict[str, Any]:
        """
        Return a structured scoring result for a given occupation.
        The score is a weighted mean of (skill importance * skill weight).
        """
        occ_data = await fetch_occupation_skills_for_scoring(self.db, occupation_id)
        skills = occ_data.get("skills", [])

        if not skills:
            raise ValueError(f"No skills found for occupation_id={occupation_id}")

        total_importance = sum(s["importance"] for s in skills)
        weighted_sum = sum(s["importance"] * s["weight"] for s in skills)

        # Simple weighted mean (later we can upgrade to percentile normalization)
        raw_score = weighted_sum / total_importance if total_importance > 0 else 0.0

        # Invert it so higher = more automatable (optional domain decision)
        automation_risk = round(min(raw_score, 100.0), 2)

        # Construct final payload
        return {
            "occupation_id": occ_data["occupation_id"],
            "occupation_label": occ_data["occupation_label"],
            "automation_risk_score": automation_risk,
            "skills_count": len(skills),
            "skills": skills,
        }

    async def bulk_score(self, occupation_ids: List[int]) -> List[Dict[str, Any]]:
        """
        Compute scores for multiple occupations in one call.
        """
        results = []
        for oid in occupation_ids:
            try:
                result = await self.get_occupation_score(oid)
                results.append(result)
            except Exception as e:
                logger.warning(f"Skipping occupation {oid}: {e}")
        return results
