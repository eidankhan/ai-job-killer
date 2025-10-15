# app/scoring/repository.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.logger import logger

# -------------------------------
# Occupation Queries
# -------------------------------

def get_occupation_by_name(db: Session, name: str) -> Optional[Dict[str, Any]]:
    """Fetch an occupation by its preferred label (case-insensitive)."""
    logger.info(f"Fetching occupation by name: {name}")
    query = text("""
        SELECT id, "preferredLabel" AS label, "conceptUri" AS uri, definition, description
        FROM occupations
        WHERE LOWER("preferredLabel") ILIKE LOWER(:name)
        LIMIT 1
    """)
    row = db.execute(query, {"name": f"%{name}%"}).mappings().first()
    if not row:
        logger.warning(f"No occupation found for name: {name}")
        return None
    logger.debug(f"Occupation found: {dict(row)}")
    return dict(row)


def list_occupations_like(db: Session, query_str: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Suggest occupations based on partial search query."""
    logger.info(f"Listing occupations like: {query_str}")
    rows = db.execute(
        text("""
            SELECT id, "preferredLabel" AS label, "conceptUri" AS uri
            FROM occupations
            WHERE LOWER("preferredLabel") ILIKE LOWER(:query)
            ORDER BY "preferredLabel" ASC
            LIMIT :limit
        """),
        {"query": f"%{query_str}%", "limit": limit}
    ).mappings().all()
    logger.debug(f"Found {len(rows)} occupations matching query '{query_str}'")
    return [dict(r) for r in rows]


# -------------------------------
# Skill Queries
# -------------------------------

def get_skills_for_occupation(db: Session, occupation_id: int) -> List[Dict[str, Any]]:
    """
    Fetch all skills linked to a given occupation, including their importance
    directly from occupation_skill_relations. Automatically normalizes importance
    if missing or invalid.
    """
    logger.info(f"Fetching skills for occupation_id={occupation_id}")

    query = text("""
        SELECT 
            s.id AS skill_id,
            s."preferredLabel" AS skill_label,
            s.definition,
            s."skillType",
            s."reuseLevel",
            COALESCE(NULLIF(osr.importance, 0), 1.0) AS importance,  -- fallback to 1.0
            osr."relationType",
            osr."skillType" AS relation_skill_type
        FROM occupation_skill_relations osr
        JOIN skills s ON s.id = osr.skill_id
        WHERE osr.occupation_id = :occupation_id
    """)

    rows = db.execute(query, {"occupation_id": occupation_id}).mappings().all()

    logger.debug(f"Found {len(rows)} skills for occupation_id={occupation_id}")

    # Extra safety: normalize and clean data
    cleaned_rows = []
    for r in rows:
        skill = dict(r)
        skill["importance"] = float(skill.get("importance") or 1.0)
        skill["skill_label"] = (skill.get("skill_label") or "").strip()
        cleaned_rows.append(skill)

    return cleaned_rows

def get_skill_by_name(db: Session, skill_name: str) -> Optional[Dict[str, Any]]:
    """Fetch skill by name (preferred or alt labels)."""
    logger.info(f"Fetching skill by name: {skill_name}")
    row = db.execute(
        text("""
            SELECT id, "preferredLabel" AS skill_label, "conceptUri", definition
            FROM skills
            WHERE LOWER("preferredLabel") ILIKE LOWER(:skill_name)
               OR LOWER("altLabels") ILIKE LOWER(:skill_name)
            LIMIT 1
        """),
        {"skill_name": f"%{skill_name}%"}
    ).mappings().first()
    if row:
        logger.debug(f"Skill found: {dict(row)}")
        return dict(row)
    logger.warning(f"No skill found for name: {skill_name}")
    return None


# -------------------------------
# Keyword Buckets
# -------------------------------

def get_bucket_keywords(db: Session) -> List[Dict[str, Any]]:
    """Retrieve all keyword → bucket mappings."""
    logger.info("Fetching bucket keywords from DB")
    rows = db.execute(
        text("""
            SELECT bk.id AS keyword_id,
                   bk.keyword,
                   bk.language,
                   sb.id AS bucket_id,
                   sb.name AS bucket_name,
                   sb.default_weight
            FROM bucket_keywords bk
            JOIN scoring_buckets sb ON sb.id = bk.bucket_id
            ORDER BY sb.id, bk.id
        """)
    ).mappings().all()
    logger.debug(f"Fetched {len(rows)} bucket keywords")
    return [dict(r) for r in rows]


def get_buckets_summary(db: Session) -> List[Dict[str, Any]]:
    """Get list of all scoring buckets with weights and short description."""
    logger.info("Fetching buckets summary")
    rows = db.execute(
        text("""
            SELECT id, name, description, default_weight, created_at
            FROM scoring_buckets
            ORDER BY id
        """)
    ).mappings().all()
    logger.debug(f"Found {len(rows)} buckets")
    return [dict(r) for r in rows]


# -------------------------------
# Automation & Importance
# -------------------------------

def get_skill_automation_scores(db: Session, skill_ids: List[int]) -> Dict[int, float]:
    """
    Dynamically compute automation risk per skill using hybrid model:
    - Uses actual table data if present
    - Falls back to bucket or metadata logic
    """
    query = text("""
        WITH bucket_based AS (
            SELECT sbm.skill_id,
                   AVG(COALESCE(sbm.weight_override, sb.default_weight)) AS bucket_weight
            FROM skill_bucket_map sbm
            JOIN scoring_buckets sb ON sb.id = sbm.bucket_id
            GROUP BY sbm.skill_id
        ),
        metadata_based AS (
            SELECT s.id AS skill_id,
                   (
                       CASE
                           WHEN s."skillType" ILIKE '%competence%' THEN 10
                           WHEN s."skillType" ILIKE '%knowledge%' THEN -10
                           ELSE 0
                       END
                       +
                       CASE
                           WHEN s."reuseLevel" ILIKE '%cross%' THEN -5
                           ELSE 0
                       END
                   )
                   *
                   (
                       CASE
                           WHEN osr."relationType" = 'essential' THEN 1.2
                           WHEN osr."relationType" = 'optional' THEN 0.8
                           ELSE 1
                       END
                   )
                   * COALESCE(osr.importance, 1.0)
                   AS metadata_weight
            FROM occupation_skill_relations osr
            JOIN skills s ON s.id = osr.skill_id
        ),
        combined AS (
            SELECT s.id AS skill_id,
                   COALESCE(sas.automation_score,
                            bucket_based.bucket_weight,
                            metadata_based.metadata_weight,
                            0) AS final_score
            FROM skills s
            LEFT JOIN skill_automation_scores sas ON sas.skill_id = s.id
            LEFT JOIN bucket_based ON bucket_based.skill_id = s.id
            LEFT JOIN metadata_based ON metadata_based.skill_id = s.id
        )
        SELECT skill_id,
               ROUND(50 + (final_score * 100), 2) AS normalized_score
        FROM combined
        WHERE skill_id = ANY(:skill_ids)
    """)

    rows = db.execute(query, {"skill_ids": skill_ids}).mappings().all()
    return {r["skill_id"]: float(r["normalized_score"]) for r in rows}



def get_occupation_skill_importance(db: Session, occupation_id: int) -> Dict[int, float]:
    logger.info(f"Fetching skill importance for occupation_id={occupation_id}")
    rows = db.execute(
        text("""
            SELECT skill_id, importance
            FROM occupation_skill_importance
            WHERE occupation_id = :occupation_id
        """),
        {"occupation_id": occupation_id}
    ).mappings().all()
    logger.debug(f"Found importance for {len(rows)} skills")
    return {r["skill_id"]: float(r["importance"]) for r in rows}


# -------------------------------
# Optional: precompute matched_buckets per skill for faster scoring
# -------------------------------

def get_skill_bucket_matches(db: Session, occupation_id: int) -> Dict[int, List[int]]:
    """
    Returns a mapping: skill_id -> list of bucket_ids it matches.
    Useful for fast computation of matched_buckets in service.py.
    """
    logger.info(f"Precomputing skill bucket matches for occupation_id={occupation_id}")
    rows = db.execute(
        text("""
            SELECT osr.skill_id, sb.id AS bucket_id
            FROM occupation_skill_relations osr
            JOIN skills s ON s.id = osr.skill_id
            JOIN bucket_keywords bk ON LOWER(bk.keyword) = ANY (string_to_array(LOWER(s."preferredLabel") || ' ' || COALESCE(s.definition, ''), ' '))
            JOIN scoring_buckets sb ON sb.id = bk.bucket_id
            WHERE osr.occupation_id = :occupation_id
        """),
        {"occupation_id": occupation_id}
    ).mappings().all()

    mapping: Dict[int, List[int]] = {}
    for r in rows:
        sid = r["skill_id"]
        bid = r["bucket_id"]
        mapping.setdefault(sid, []).append(bid)
    logger.debug(f"Computed matched_buckets for {len(mapping)} skills")
    return mapping
