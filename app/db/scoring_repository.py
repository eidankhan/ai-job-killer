# app/db/repositories.py
from typing import Any, Dict, List
from decimal import Decimal
import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

# Default fallback weight if nothing matches
DEFAULT_FALLBACK_WEIGHT = 5.0

async def fetch_occupation_skills_for_scoring(db: AsyncSession, occupation_id: int) -> Dict[str, Any]:
    """
    Fetch occupation label and skill list for the given occupation_id.

    Each skill row will include:
      - skill_id
      - skill_label
      - definition
      - importance (float)
      - weight (float) : the numeric weight chosen for scoring
      - mapping_source (str) : 'explicit_map'|'precomputed_score'|'keyword_fallback'|'default'
      - weight_source (str) : 'explicit_override'|'bucket_default'|'automation_score'|'default'
      - bucket_id (int|null) : the bucket id when applicable

    The function prefers the following resolution order:
      1) explicit skill_bucket_map (weight_override or bucket default)
      2) precomputed automation score (skill_automation_scores.automation_score)
      3) keyword fallback -> bucket default weight (bucket_keywords -> scoring_buckets)
      4) default fallback weight (DEFAULT_FALLBACK_WEIGHT)

    Returns a dict suitable for passing to the scoring layer.
    Raises ValueError if occupation_id not found.
    """
    # 1) fetch occupation label
    occ_sql = text(
        """
        SELECT id, COALESCE("preferredLabel", "conceptUri") AS occupation_label
        FROM occupations
        WHERE id = :occupation_id
        """
    )
    occ_res = await db.execute(occ_sql, {"occupation_id": occupation_id})
    occ_row = occ_res.mappings().first()
    if not occ_row:
        raise ValueError(f"Occupation id={occupation_id} not found")

    # 2) Fetch skills with explicit mapping + automation score + keyword fallback (single keyword hit)
    # Note: we alias skill columns to snake_case for easy consumption
    skills_sql = text(
        """
        WITH occ_skills AS (
          SELECT osr.skill_id,
                 COALESCE(osr.importance, 1.0) AS importance,
                 s."preferredLabel" AS preferred_label,
                 s.definition AS definition
          FROM occupation_skill_relations osr
          JOIN skills s ON s.id = osr.skill_id
          WHERE osr.occupation_id = :occupation_id
        )
        SELECT
          os.skill_id,
          os."preferred_label",
          os.definition,
          os.importance,
          sbm.bucket_id                 AS explicit_bucket_id,
          sbm.weight_override           AS weight_override,
          sbm.map_source                AS map_source,
          sb.default_weight             AS explicit_bucket_default_weight,
          sas.automation_score          AS automation_score,
          bk_match.bucket_id            AS keyword_bucket_id,
          sbk.default_weight            AS keyword_bucket_default_weight
        FROM occ_skills os
        LEFT JOIN skill_bucket_map sbm ON sbm.skill_id = os.skill_id
        LEFT JOIN scoring_buckets sb ON sb.id = sbm.bucket_id
        LEFT JOIN skill_automation_scores sas ON sas.skill_id = os.skill_id
        LEFT JOIN LATERAL (
          SELECT bk.bucket_id
          FROM bucket_keywords bk
          WHERE to_tsvector('simple', COALESCE(os."preferred_label",'') || ' ' || COALESCE(os.definition,'')) @@ plainto_tsquery(bk.keyword)
          LIMIT 1
        ) bk_match ON true
        LEFT JOIN scoring_buckets sbk ON sbk.id = bk_match.bucket_id
        """
    )

    res = await db.execute(skills_sql, {"occupation_id": occupation_id})
    rows = res.mappings().all()

    skills: List[Dict[str, Any]] = []
    for r in rows:
        skill_id = r["skill_id"]
        skill_label = r["preferred_label"] or None
        definition = r["definition"] or None
        importance = float(r["importance"]) if r["importance"] is not None else 1.0

        explicit_bucket_id = r.get("explicit_bucket_id")
        weight_override = r.get("weight_override")
        explicit_bucket_default_weight = r.get("explicit_bucket_default_weight")
        automation_score = r.get("automation_score")
        keyword_bucket_id = r.get("keyword_bucket_id")
        keyword_bucket_default_weight = r.get("keyword_bucket_default_weight")

        chosen_weight = None
        mapping_source = "default"
        weight_source = "default"
        chosen_bucket_id = None

        # Priority 1: explicit skill_bucket_map
        if explicit_bucket_id is not None:
            chosen_bucket_id = explicit_bucket_id
            if weight_override is not None:
                # weight_override may be Decimal
                chosen_weight = float(weight_override) if not isinstance(weight_override, float) else weight_override
                weight_source = "explicit_override"
            elif explicit_bucket_default_weight is not None:
                chosen_weight = float(explicit_bucket_default_weight)
                weight_source = "bucket_default"
            else:
                chosen_weight = DEFAULT_FALLBACK_WEIGHT
                weight_source = "default"
            mapping_source = r.get("map_source") or "explicit_map"

        # Priority 2: precomputed automation score
        elif automation_score is not None:
            # automation_score might be decimal
            chosen_weight = float(automation_score)
            mapping_source = "precomputed_score"
            weight_source = "automation_score"

        # Priority 3: keyword fallback -> bucket default
        elif keyword_bucket_id is not None:
            chosen_bucket_id = keyword_bucket_id
            if keyword_bucket_default_weight is not None:
                chosen_weight = float(keyword_bucket_default_weight)
                weight_source = "bucket_default"
            else:
                chosen_weight = DEFAULT_FALLBACK_WEIGHT
                weight_source = "default"
            mapping_source = "keyword_fallback"

        # Priority 4: default fallback
        else:
            chosen_weight = DEFAULT_FALLBACK_WEIGHT
            mapping_source = "default"
            weight_source = "default"

        # Ensure numeric types
        if isinstance(chosen_weight, Decimal):
            chosen_weight = float(chosen_weight)

        skills.append(
            {
                "skill_id": skill_id,
                "skill_label": skill_label,
                "definition": definition,
                "importance": float(importance),
                "weight": float(chosen_weight),
                "mapping_source": mapping_source,
                "weight_source": weight_source,
                "bucket_id": int(chosen_bucket_id) if chosen_bucket_id is not None else None,
            }
        )

    return {
        "occupation_id": int(occ_row["id"]),
        "occupation_label": occ_row["occupation_label"],
        "skills": skills,
    }
