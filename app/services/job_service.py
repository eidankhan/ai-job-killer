# import os
# import pandas as pd
# from sqlalchemy.orm import Session
# from app.models.profession import Profession
# from app.models.skill import Skill
# from app.models.profession import Profession
# from rapidfuzz import process, fuzz

# # Paths relative to project root
# DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
# OCCUPATION_FILE = os.path.join(DATA_DIR, "OccupationData.txt")
# SKILLS_FILE = os.path.join(DATA_DIR, "Skills.txt")

# def ingest_onet_data(db: Session, importance_threshold: float = 0.0, force: bool = False):
#     """
#     Load O*NET Occupation & Skills data into DB.
#     Skips if already loaded unless force=True.
#     """

#     # Prevent re-import if data already loaded
#     if not force and db.query(Profession).count() > 0:
#         return {"status": "skipped", "message": "Professions already loaded"}

#     # Validate file existence
#     for path in [OCCUPATION_FILE, SKILLS_FILE]:
#         if not os.path.exists(path):
#             raise FileNotFoundError(f"Required file not found: {path}")

#     print("[ETL] Reading O*NET files...")

#     # Read Occupations
#     occ_df = pd.read_csv(OCCUPATION_FILE, sep="\t", dtype=str, usecols=["O*NET-SOC Code", "Title", "Description"])

#     # Read Skills
#     skills_df = pd.read_csv(SKILLS_FILE, sep="\t", dtype=str, usecols=["O*NET-SOC Code", "Element Name", "Scale ID", "Data Value"])
#     skills_df = skills_df[skills_df["Scale ID"] == "IM"]  # keep importance scale only
#     skills_df["Data Value"] = skills_df["Data Value"].astype(float)

#     if importance_threshold > 0:
#         skills_df = skills_df[skills_df["Data Value"] >= importance_threshold]

#     # Merge to get job title + description with skills
#     merged = (
#         skills_df
#         .merge(occ_df, on="O*NET-SOC Code", how="left")
#         .dropna(subset=["Title"])  # drop skills with no matching occupation
#     )

#     # Group skills by profession
#     grouped = merged.groupby(["Title", "Description"])["Element Name"].apply(list).reset_index()

#     # Clear existing data if force reload
#     if force:
#         db.query(Skill).delete()
#         db.query(Profession).delete()
#         db.commit()

#     print(f"[ETL] Loading {len(grouped)} professions into DB...")

#     for _, row in grouped.iterrows():
#         prof = Profession(title=row["Title"], description=row["Description"])
#         db.add(prof)
#         db.flush()  # get ID

#         for skill_name in row["Element Name"]:
#             db.add(Skill(name=skill_name, profession_id=prof.id, risk_level="safe"))

#     db.commit()
#     return {"status": "success", "message": f"Loaded {len(grouped)} professions"}


# def search_professions(db: Session, query: str, limit: int = 10):
#     titles = [p.title for p in db.query(Profession).all()]
#     matches = process.extract(query, titles, scorer=fuzz.WRatio, limit=limit)
#     results = []
#     for title, score, _ in matches:
#         prof = db.query(Profession).filter_by(title=title).first()
#         if prof:
#             results.append({"id": prof.id, "title": prof.title, "score": score})
#     return results
