# import os
# import pandas as pd
# from typing import Dict, Callable, List, Any, Set
# from sqlalchemy.orm import Session
# from sqlalchemy.dialects.postgresql import insert
# from sqlalchemy import func
# from fastapi import HTTPException

# from app.utils.text_utils import parse_date
# from app.models.skill import Skill
# from app.models.skill_group import SkillGroup
# from app.models.skill_hierarchy import SkillHierarchy
# from app.models.occupation import Occupation
# from app.models.occupation_skill import OccupationSkill

# CLEANED_DIR = "/app/cleaned_data"
# DEFAULT_CHUNK = 500


# # ---------- Low-level helpers ----------
# def _get_unique_keys(model) -> List[str]:
#     """Return the first unique constraint column list if defined."""
#     if hasattr(model.__table__, "constraints"):
#         for c in model.__table__.constraints:
#             if getattr(c, "columns", None) and getattr(c, "name", None) and "uq_" in c.name:
#                 return [col.name for col in c.columns]
#     # fallback to primary key
#     return ["id"]


# def _upsert_chunk(db: Session, model, rows: List[Dict[str, Any]]) -> int:
#     """Bulk upsert using ON CONFLICT based on unique constraints."""
#     if not rows:
#         return 0

#     stmt = insert(model.__table__).values(rows)
#     unique_keys = _get_unique_keys(model)
#     update_dict = {
#         c.name: getattr(stmt.excluded, c.name)
#         for c in model.__table__.columns
#         if c.name not in unique_keys and c.name != "id"
#     }
#     stmt = stmt.on_conflict_do_update(index_elements=unique_keys, set_=update_dict)
#     db.execute(stmt)
#     db.commit()
#     return len(rows)


# def _insert_chunk(db: Session, model, rows: List[Dict[str, Any]]) -> int:
#     if not rows:
#         return 0
#     stmt = insert(model.__table__).values(rows)
#     db.execute(stmt)
#     db.commit()
#     return len(rows)


# def _table_has_rows(db: Session, model) -> int:
#     return db.query(func.count()).select_from(model.__table__).scalar() or 0


# def _read_chunks(path: str, chunksize: int = DEFAULT_CHUNK):
#     for chunk in pd.read_csv(path, dtype=str, keep_default_na=False, chunksize=chunksize):
#         yield chunk


# def _get_existing_concept_uris(db: Session, model, column_name: str = "concept_uri") -> Set[str]:
#     rows = db.query(getattr(model, column_name)).all()
#     return {r[0] for r in rows if r and r[0]}


# # ---------- Row preparation ----------
# def _prepare_skills_chunk(df: pd.DataFrame) -> List[Dict[str, Any]]:
#     return [
#         {
#             "concept_uri": r.get("conceptUri") or None,
#             "skill_type": r.get("skillType") or None,
#             "reuse_level": r.get("reuseLevel") or None,
#             "preferred_label": r.get("preferredLabel") or None,
#             "alt_labels": r.get("altLabels") or None,
#             "hidden_labels": r.get("hiddenLabels") or None,
#             "status": r.get("status") or None,
#             "modified_date": parse_date(r.get("modifiedDate")),
#             "scope_note": r.get("scopeNote") or None,
#             "definition": r.get("definition") or None,
#             "in_scheme": r.get("inScheme") or None,
#             "description": r.get("description") or None,
#         } for _, r in df.iterrows()
#     ]


# def _prepare_skill_groups_chunk(df: pd.DataFrame) -> List[Dict[str, Any]]:
#     return [
#         {
#             "concept_uri": r.get("conceptUri") or None,
#             "preferred_label": r.get("preferredLabel") or None,
#             "alt_labels": r.get("altLabels") or None,
#             "hidden_labels": r.get("hiddenLabels") or None,
#             "status": r.get("status") or None,
#             "modified_date": parse_date(r.get("modifiedDate")),
#             "scope_note": r.get("scopeNote") or None,
#             "in_scheme": r.get("inScheme") or None,
#             "description": r.get("description") or None,
#             "code": r.get("code") or None,
#         } for _, r in df.iterrows()
#     ]


# def _prepare_skill_hierarchy_chunk(df: pd.DataFrame) -> List[Dict[str, Any]]:
#     return [
#         {
#             "level_0_uri": r.get("Level 0 URI") or None,
#             "level_0_label": r.get("Level 0 preferred term") or None,
#             "level_1_uri": r.get("Level 1 URI") or None,
#             "level_1_label": r.get("Level 1 preferred term") or None,
#             "level_2_uri": r.get("Level 2 URI") or None,
#             "level_2_label": r.get("Level 2 preferred term") or None,
#             "level_3_uri": r.get("Level 3 URI") or None,
#             "level_3_label": r.get("Level 3 preferred term") or None,
#             "description": r.get("Description") or None,
#             "scope_note": r.get("Scope note") or None,
#             "level_0_code": r.get("Level 0 code") or None,
#             "level_1_code": r.get("Level 1 code") or None,
#             "level_2_code": r.get("Level 2 code") or None,
#             "level_3_code": r.get("Level 3 code") or None,
#         } for _, r in df.iterrows()
#     ]


# def _prepare_occupations_chunk(df: pd.DataFrame) -> List[Dict[str, Any]]:
#     return [
#         {
#             "concept_uri": r.get("conceptUri") or None,
#             "isco_group": r.get("iscoGroup") or None,
#             "preferred_label": r.get("preferredLabel") or None,
#             "alt_labels": r.get("altLabels") or None,
#             "hidden_labels": r.get("hiddenLabels") or None,
#             "status": r.get("status") or None,
#             "modified_date": parse_date(r.get("modifiedDate")),
#             "regulated_note": r.get("regulatedProfessionNote") or None,
#             "scope_note": r.get("scopeNote") or None,
#             "definition": r.get("definition") or None,
#             "in_scheme": r.get("inScheme") or None,
#             "description": r.get("description") or None,
#             "code": r.get("code") or None,
#         } for _, r in df.iterrows()
#     ]


# def _prepare_occupation_skills_chunk(df: pd.DataFrame) -> List[Dict[str, Any]]:
#     return [
#         {
#             "occupation_uri": r.get("occupationUri") or None,
#             "skill_uri": r.get("skillUri") or None,
#             "relation_type": r.get("relationType") or None,
#             "skill_type": r.get("skillType") or None,
#         } for _, r in df.iterrows()
#     ]


# # ---------- Main Orchestrator ----------
# def import_all_data(db: Session, chunksize: int = DEFAULT_CHUNK) -> Dict[str, Any]:
#     report: Dict[str, Any] = {}

#     file_map = {
#         "skills": ("cleaned_Skills_en.csv", _prepare_skills_chunk, Skill),
#         "skill_groups": ("cleaned_SkillGroups_en.csv", _prepare_skill_groups_chunk, SkillGroup),
#         "skill_hierarchy": ("cleaned_SkillHierarchy_en.csv", _prepare_skill_hierarchy_chunk, SkillHierarchy),
#         "occupations": ("cleaned_Occupations_en.csv", _prepare_occupations_chunk, Occupation),
#         "occupation_skills": ("cleaned_OccupationSkillsRelation_en.csv", _prepare_occupation_skills_chunk, OccupationSkill),
#     }

#     process_order = [ "occupations", "occupation_skills", "skills", "skill_groups", "skill_hierarchy"]

#     for key in process_order:
#         fname, prepare_fn, model = file_map[key]
#         path = os.path.join(CLEANED_DIR, fname)

#         if not os.path.exists(path):
#             report[key] = {"status": "skipped", "reason": f"{fname} not found"}
#             continue

#         try:
#             existing_count = _table_has_rows(db, model)
#         except Exception as e:
#             report[key] = {"status": "failed", "error": f"DB checkpoint failed: {e}"}
#             continue

#         if existing_count > 0:
#             report[key] = {"status": "skipped", "rows_existing": existing_count}
#             continue

#         total_in, total_processed, total_dropped = 0, 0, 0

#         try:
#             existing_occs = _get_existing_concept_uris(db, Occupation) if key == "occupation_skills" else set()
#             existing_skills = _get_existing_concept_uris(db, Skill) if key == "occupation_skills" else set()

#             for chunk_df in _read_chunks(path, chunksize):
#                 total_in += len(chunk_df)
#                 rows = prepare_fn(chunk_df)

#                 if key == "occupation_skills":
#                     valid_rows, dropped = [], 0
#                     for r in rows:
#                         if r["occupation_uri"] in existing_occs and r["skill_uri"] in existing_skills:
#                             valid_rows.append(r)
#                         else:
#                             dropped += 1
#                     total_dropped += dropped
#                     rows_to_write = valid_rows
#                 else:
#                     rows_to_write = rows

#                 if not rows_to_write:
#                     continue

#                 processed = _upsert_chunk(db, model, rows_to_write)
#                 total_processed += processed

#             tbl_report = {"status": "ok", "rows_in_file": total_in, "rows_written": total_processed}
#             if total_dropped:
#                 tbl_report["dropped_invalid_relations"] = total_dropped
#             report[key] = tbl_report

#         except Exception as e:
#             db.rollback()
#             report[key] = {"status": "failed", "error": str(e)}

#     # Decide HTTP response
#     all_failed = all(r["status"] == "failed" for r in report.values())
#     any_failed = any(r["status"] == "failed" for r in report.values())

#     if all_failed:
#         raise HTTPException(status_code=500, detail={"import_report": report})
#     elif any_failed:
#         raise HTTPException(status_code=207, detail={"import_report": report})

#     return {"import_report": report}
