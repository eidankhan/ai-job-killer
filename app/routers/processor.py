# from fastapi import APIRouter
# from fastapi.responses import JSONResponse
# import os
# from app.services.file_io import read_csv_file, save_cleaned_csv
# from app.services.cleaners import CLEANER_MAP

# router = APIRouter()

# DATA_DIR = "/app/data"

# # Path inside the container to project root (/app)
# PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# # Cleaned dir inside project root (/app/cleaned)
# CLEANED_DIR = os.path.join(PROJECT_ROOT, "cleaned_data")
# os.makedirs(CLEANED_DIR, exist_ok=True)


# @router.post("/data/process")
# async def process_all_data():
#     """
#     Clean all ESCO CSV files from /data and save to /cleaned.
#     Returns a JSON summary report.
#     """
#     report = {}

#     file_map = {
#         "occupations": "Occupations_en.csv",
#         "skills": "Skills_en.csv",
#         "occupation_skills_relation": "OccupationSkillsRelation_en.csv",
#         "skill_groups": "SkillGroups_en.csv",
#         "skill_hierarchy": "SkillHierarchy_en.csv",
#     }

#     for key, filename in file_map.items():
#         path = os.path.join(DATA_DIR, filename)
#         if not os.path.exists(path):
#             report[key] = {"error": f"File not found: {filename}"}
#             continue

#         try:
#             df = read_csv_file(path)
#             cleaner = CLEANER_MAP[key]
#             file_report = {"original_rows": len(df)}

#             cleaned = cleaner(df.copy(), file_report)
#             file_report["rows_out"] = len(cleaned)

#             save_path = os.path.join(CLEANED_DIR, f"cleaned_{filename}")
#             save_cleaned_csv(cleaned, save_path)

#             report[key] = file_report

#         except Exception as e:
#             report[key] = {"error": str(e)}

#     return JSONResponse(content={"summary": report, "cleaned_dir": CLEANED_DIR})
