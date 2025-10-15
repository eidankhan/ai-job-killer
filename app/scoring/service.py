# app/scoring/service.py
from typing import Any, Dict, List, Optional
from app.core.logger import logger
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.scoring import repository as repo

# Tunable parameters
DEFAULT_FALLBACK_WEIGHT = 5.0
ALPHA = 1.0  # how strongly "safe" offsets positive risk
EPS = 1e-9


def vulnerability_label_normalized(normalized: float) -> str:
    """Map normalized contribution to a human-readable label with adjusted thresholds."""
    if normalized >= 0.9:
        return "Very High"
    elif normalized >= 0.7:
        return "High"
    elif normalized >= 0.4:
        return "Moderate"
    elif normalized > 0:
        return "Low"
    elif normalized <= 0.2:
        return "Safe"
    else:
        return "Neutral"


def vuln_factor_from_label(label: str) -> float:
    """Assign numeric vulnerability factor based on label (0.0..1.0)."""
    mapping = {
        "Very High": 1.0,
        "High": 0.75,
        "Moderate": 0.5,
        "Low": 0.25,
        "Safe": 0.0,
        "Neutral": 0.5,
    }
    return mapping.get(label, 0.5)


def compute_risk_from_contribs_normalized(per_skill_items: List[dict]) -> float:
    """Compute 0..100 risk score using normalized contributions and vuln_factor."""
    if not per_skill_items:
        return 50.0  # neutral if no skills

    raw_values = [s["raw_contrib"] for s in per_skill_items]
    min_val = min(raw_values)
    max_val = max(raw_values)
    range_val = max_val - min_val + 1e-8  # avoid division by zero

    for item in per_skill_items:
        normalized = (item["raw_contrib"] - min_val) / range_val
        item["normalized_contrib"] = normalized
        item["vulnerability"] = vulnerability_label_normalized(normalized)
        item["vuln_factor"] = vuln_factor_from_label(item["vulnerability"])

    risk_score = sum(item["normalized_contrib"] * item["vuln_factor"] for item in per_skill_items)
    return max(0.0, min(100.0, risk_score * 100))


class SimpleDbDrivenScorer:
    """DB-driven scoring service with optimized bucket matching."""

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
                    "keywords": set(),
                }
            kw = r["keyword"]
            if kw:
                buckets[b_id]["keywords"].add(kw.lower())

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
        return self.score_by_occupation_id(db, int(occ["id"]))


    def score_by_occupation_id(
        self, db: Session, occupation_id: int, sort_by: str = "normalized_contrib"
    ) -> dict:
        """Compute risk score for an occupation using normalized contributions and vulnerability factors."""
        logger.info(f"Scoring occupation id={occupation_id}")

        # Fetch occupation label
        occ_row = db.execute(
            text('SELECT "preferredLabel" AS label FROM occupations WHERE id = :occupation_id'),
            {"occupation_id": occupation_id}
        ).mappings().first()
        if not occ_row:
            raise ValueError(f"Occupation id={occupation_id} not found")
        occupation_label = occ_row["label"] or f"occupation:{occupation_id}"
        logger.debug(f"Occupation label: {occupation_label}")

        # Fetch skills
        skills = repo.get_skills_for_occupation(db, occupation_id)
        if not skills:
            logger.info(f"No skills for occupation id={occupation_id}, returning neutral score")
            return {
                "occupation_id": occupation_id,
                "occupation_label": occupation_label,
                "risk_score": 50.0,
                "level": "Yellow",
                "explanation": "No skills available; returned neutral score",
                "skills_analyzed": 0,
                "per_skill": [],
                "matched_buckets": {},
            }

        skill_ids = [s["skill_id"] for s in skills]
        automation_map = repo.get_skill_automation_scores(db, skill_ids)
        buckets = self._load_bucket_keywords(db)
        skill_bucket_map = repo.get_skill_bucket_matches(db, occupation_id)

        per_skill_items: list[dict] = []
        matched_buckets_counts: dict[int, int] = {}

        # Step 1: Compute raw contributions
        raw_contribs: list[float] = []
        for s in skills:
            sid = int(s["skill_id"])
            label = (s.get("skill_label") or "").strip() or f"skill:{sid}"
            definition = s.get("definition") or ""
            importance = float(s.get("importance") or 1.0)

            chosen_weight = DEFAULT_FALLBACK_WEIGHT
            mapping_source = "default"
            weight_source = "default"
            chosen_bucket_id = None

            if sid in automation_map:
                chosen_weight = float(automation_map[sid])
                mapping_source = "precomputed_score"
                weight_source = "automation_score"
            else:
                matched_buckets = skill_bucket_map.get(sid, [])
                if matched_buckets:
                    chosen_bucket_id = matched_buckets[0]
                    b_meta = buckets[chosen_bucket_id]
                    chosen_weight = float(b_meta["default_weight"])
                    mapping_source = "keyword_bucket"
                    weight_source = "bucket_default"
                    for bid in matched_buckets:
                        matched_buckets_counts[bid] = matched_buckets_counts.get(bid, 0) + 1

            contrib = chosen_weight * importance
            raw_contribs.append(contrib)

            per_skill_items.append({
                "skill_id": sid,
                "skill_label": label,
                "definition": definition,
                "importance": importance,
                "weight": chosen_weight,
                "mapping_source": mapping_source,
                "weight_source": weight_source,
                "bucket_id": int(chosen_bucket_id) if chosen_bucket_id is not None else None,
                "raw_contrib": contrib,
                "weighted_contrib": contrib,  # optional: for table output
            })

        # Step 2: Normalize contributions
        min_contrib = min(raw_contribs)
        max_contrib = max(raw_contribs)
        range_contrib = max_contrib - min_contrib + 1e-8  # prevent zero division

        for item in per_skill_items:
            normalized = (item["raw_contrib"] - min_contrib) / range_contrib
            item["normalized_contrib"] = normalized
            item["vulnerability"] = vulnerability_label_normalized(normalized)

        # Step 3: Compute overall risk
        risk_score = compute_risk_from_contribs_normalized(per_skill_items)
        level = (
            "Green" if risk_score < 30
            else "Yellow" if risk_score <= 70
            else "Red"
        )

        # Step 4: Sort per skill
        if sort_by in {"raw_contrib", "normalized_contrib", "weight", "importance"}:
            per_skill_items.sort(key=lambda x: x[sort_by], reverse=True)

        # Step 5: Build explanation with top 5 vulnerable and top 5 safe skills
        top_vulnerable = [p["skill_label"] for p in per_skill_items if p["normalized_contrib"] > 0.6][:5]
        top_safe = [p["skill_label"] for p in per_skill_items if p["normalized_contrib"] <= 0.3][:5]

        explanation_parts = []
        if top_vulnerable:
            explanation_parts.append(f"Top vulnerable skills: {', '.join(top_vulnerable)}")
        if top_safe:
            explanation_parts.append(f"Safe skills: {', '.join(top_safe)}")
        explanation = " — ".join(explanation_parts) if explanation_parts else "Mixed profile"

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
