from typing import Any, Dict, List, Optional
from app.core.logger import logger
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.scoring import repository as repo

# Tunable parameters
DEFAULT_FALLBACK_WEIGHT = 5.0
ALPHA = 1.0  # how strongly "safe" offsets positive risk
EPS = 1e-9


def vulnerability_label(weight: float) -> str:
    """Human-friendly vulnerability label for a single skill weight."""
    if weight >= 20:
        return "High"
    if weight >= 10:
        return "Medium"
    if weight > 0:
        return "Low"
    return "Safe"


def compute_risk_from_contribs(contribs: List[float], alpha: float = ALPHA) -> float:
    """Compute a 0..100 risk score using positive/negative separation."""
    positive = sum(c for c in contribs if c > 0)
    negative = sum(-c for c in contribs if c < 0)
    denom = positive + alpha * negative + EPS
    if denom <= 0:
        return 0.0
    score = 100.0 * (positive / denom)
    logger.debug(f"Computed risk from contribs: positive={positive}, negative={negative}, score={score}")
    return max(0.0, min(100.0, score))


class SimpleDbDrivenScorer:
    """DB-driven scoring service for minimal scoring pipeline."""

    def __init__(self):
        self._bucket_keywords_cache: Optional[Dict[int, Dict[str, Any]]] = None

    def _load_bucket_keywords(self, db: Session) -> Dict[int, Dict[str, Any]]:
        """Load bucket keywords & metadata from DB and cache."""
        if self._bucket_keywords_cache:
            logger.debug("Using cached bucket keywords")
            return self._bucket_keywords_cache

        logger.info("Loading bucket keywords from DB")
        rows = repo.get_bucket_keywords(db)
        buckets: Dict[int, Dict[str, Any]] = {}
        for r in rows:
            b_id = int(r["bucket_id"])
            if b_id not in buckets:
                buckets[b_id] = {
                    "bucket_id": b_id,
                    "bucket_name": r["bucket_name"],
                    "default_weight": float(r["default_weight"]) if r["default_weight"] is not None else DEFAULT_FALLBACK_WEIGHT,
                    "keywords": [],
                }
            kw = r["keyword"]
            if kw:
                buckets[b_id]["keywords"].append(kw.lower())

        self._bucket_keywords_cache = buckets
        logger.debug(f"Loaded {len(buckets)} buckets with keywords")
        return buckets

    def score_by_occupation_name(self, db: Session, occupation_name: str) -> Dict[str, Any]:
        """Compute score using occupation name (fuzzy match)."""
        logger.info(f"Scoring by occupation name: {occupation_name}")
        occ = repo.get_occupation_by_name(db, occupation_name)
        if not occ:
            logger.warning(f"Occupation matching '{occupation_name}' not found")
            raise ValueError(f"Occupation matching '{occupation_name}' not found")

        occ_id = int(occ["id"])
        return self.score_by_occupation_id(db, occ_id)

    def score_by_occupation_id(self, db: Session, occupation_id: int) -> Dict[str, Any]:
        """Compute score given occupation_id using DB-driven skill weights."""
        logger.info(f"Scoring occupation id={occupation_id}")

        # fetch occupation label
        try:
            occ_res = db.execute(
                text('SELECT id, "preferredLabel" AS label FROM occupations WHERE id = :occupation_id'),
                {"occupation_id": occupation_id},
            ).mappings()
            occ_row = occ_res.first()
            if not occ_row:
                logger.warning(f"Occupation id={occupation_id} not found")
                raise ValueError(f"Occupation id={occupation_id} not found")
            occupation_label = occ_row["label"] or f"occupation:{occupation_id}"
            logger.debug(f"Occupation label: {occupation_label}")
        except Exception as e:
            logger.error(f"Error fetching occupation id={occupation_id}: {e}")
            raise

        # fetch skills
        skills = repo.get_skills_for_occupation(db, occupation_id)
        logger.debug(f"Found {len(skills)} skills for occupation id={occupation_id}")
        if not skills:
            logger.info(f"No skills found for occupation id={occupation_id}, returning neutral score")
            return {
                "occupation_id": occupation_id,
                "occupation_label": occupation_label,
                "risk_score": 50.0,
                "level": "Yellow",
                "explanation": "No skills available; returned neutral score",
                "skills_analyzed": 0,
                "per_skill": [],
            }

        # importance map and automation scores
        importance_map = repo.get_occupation_skill_importance(db, occupation_id)
        skill_ids = [s["skill_id"] for s in skills]
        automation_map = repo.get_skill_automation_scores(db, skill_ids)
        logger.debug(f"Loaded importance and automation scores for {len(skill_ids)} skills")

        # bucket keywords
        buckets = self._load_bucket_keywords(db)

        per_skill_items: List[Dict[str, Any]] = []
        contribs: List[float] = []
        matched_buckets_counts: Dict[int, int] = {}

        for s in skills:
            sid = int(s["skill_id"])
            label = (s.get("skill_label") or "").strip() or f"skill:{sid}"
            definition = s.get("definition") or ""
            importance = float(s.get("importance") or importance_map.get(sid) or 1.0)

            chosen_weight: float = DEFAULT_FALLBACK_WEIGHT
            mapping_source = "default"
            weight_source = "default"
            chosen_bucket_id = None

            # 1️⃣ precomputed automation score
            if sid in automation_map:
                chosen_weight = float(automation_map[sid])
                mapping_source = "precomputed_score"
                weight_source = "automation_score"
            else:
                # 2️⃣ keyword bucket match
                text_to_search = f"{label} {definition}".lower()
                matched = False
                for b_id, b_meta in buckets.items():
                    for kw in b_meta["keywords"]:
                        if kw in text_to_search:
                            chosen_bucket_id = b_id
                            chosen_weight = float(b_meta["default_weight"])
                            mapping_source = "keyword_bucket"
                            weight_source = "bucket_default"
                            matched_buckets_counts[b_id] = matched_buckets_counts.get(b_id, 0) + 1
                            matched = True
                            break
                    if matched:
                        break

            contrib = chosen_weight * importance
            contribs.append(contrib)

            per_skill_items.append(
                {
                    "skill_id": sid,
                    "skill_label": label,
                    "definition": definition,
                    "importance": importance,
                    "weight": chosen_weight,
                    "mapping_source": mapping_source,
                    "weight_source": weight_source,
                    "bucket_id": int(chosen_bucket_id) if chosen_bucket_id is not None else None,
                    "contrib": contrib,
                    "vulnerability": vulnerability_label(chosen_weight),
                }
            )

        risk_score = compute_risk_from_contribs(contribs)
        level = "Green" if risk_score < 30 else "Yellow" if risk_score <= 70 else "Red"

        # top vulnerable & safe skills
        sorted_by_contrib = sorted(per_skill_items, key=lambda x: x["contrib"], reverse=True)
        top_vulnerable = [p["skill_label"] for p in sorted_by_contrib if p["contrib"] > 0][:3]
        top_safe = [p["skill_label"] for p in sorted_by_contrib if p["contrib"] <= 0][:3]

        explanation_parts = []
        if top_vulnerable:
            explanation_parts.append(f"Top vulnerable skills: {', '.join(top_vulnerable)}")
        if top_safe:
            explanation_parts.append(f"Safe skills: {', '.join(top_safe)}")
        explanation = " — ".join(explanation_parts) if explanation_parts else "Mixed profile"

        logger.info(f"Computed risk score={risk_score:.2f} for occupation_id={occupation_id}")
        return {
            "occupation_id": occupation_id,
            "occupation_label": occupation_label,
            "risk_score": round(risk_score, 2),
            "level": level,
            "explanation": explanation,
            "skills_analyzed": len(per_skill_items),
            "matched_buckets": matched_buckets_counts,
            "per_skill": per_skill_items,
        }
