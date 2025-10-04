# #!/bin/bash
# set -e

# echo "Loading ESCO data into Postgres..."

# DATA_DIR="/docker-entrypoint-initdb.d/ESCO-dataset-v1.1.1"

# # 1. Load Occupations
# echo "Loading occupations..."
# psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\COPY public.occupations(
#     concept_type,
#     concept_uri,
#     isco_group,
#     preferred_label,
#     alt_labels,
#     hidden_labels,
#     status,
#     modified_date,
#     regulated_note,
#     scope_note,
#     definition,
#     in_scheme,
#     description,
#     code
# ) FROM '${DATA_DIR}/occupations_en.csv' CSV HEADER"

# # 2. Load Skills
# echo "Loading skills..."
# psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\COPY public.skills(
#     concept_type,
#     concept_uri,
#     skill_type,
#     reuse_level,
#     preferred_label,
#     alt_labels,
#     hidden_labels,
#     status,
#     modified_date,
#     scope_note,
#     definition,
#     in_scheme,
#     description
# ) FROM '${DATA_DIR}/skills_en.csv' CSV HEADER"

# # 3. Filter occupation-skill relations to only valid FKs
# echo "Filtering and loading occupation-skill relations..."
# cut -d',' -f2 "${DATA_DIR}/occupations_en.csv" | tail -n +2 > /tmp/valid_occupations.txt
# cut -d',' -f2 "${DATA_DIR}/skills_en.csv" | tail -n +2 > /tmp/valid_skills.txt

# awk -F',' 'NR==FNR {occ[$1]; next} NR==FNR+FNR {skill[$1]; next} ($1 in occ) && ($4 in skill)' \
#     /tmp/valid_occupations.txt /tmp/valid_skills.txt "${DATA_DIR}/occupationSkillRelations_en.csv" \
#     > /tmp/filtered_occupationSkillRelations_en.csv

# psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\COPY public.occupation_skill_relations(
#     occupation_uri,
#     relation_type,
#     skill_type,
#     skill_uri
# ) FROM '/tmp/filtered_occupationSkillRelations_en.csv' CSV HEADER"

# # 4. Load Skill Groups
# echo "Loading skill groups..."
# psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\COPY public.skill_groups(
#     concept_type,
#     concept_uri,
#     preferred_label,
#     alt_labels,
#     hidden_labels,
#     status,
#     modified_date,
#     scope_note,
#     in_scheme,
#     description,
#     code
# ) FROM '${DATA_DIR}/skillGroups_en.csv' CSV HEADER"

# # 5. Load Skill Hierarchy
# echo "Loading skill hierarchy..."
# # Step 5.1: Remove carriage returns (\r)
# tr -d '\r' < "${DATA_DIR}/skillsHierarchy_en.csv" > /tmp/skillsHierarchy_clean.csv

# # Step 5.2: Pad missing columns to exactly 14 using awk
# awk -F',' 'BEGIN {OFS=","} 
# NR==1 {print; next} 
# {
#     while (NF < 14) $++NF="";
#     print
# }' /tmp/skillsHierarchy_clean.csv > /tmp/skillsHierarchy_padded.csv

# # Step 5.3: Load into Postgres
# psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "\COPY public.skill_hierarchy(
#     level_0_uri,
#     level_0_label,
#     level_1_uri,
#     level_1_label,
#     level_2_uri,
#     level_2_label,
#     level_3_uri,
#     level_3_label,
#     description,
#     scope_note,
#     level_0_code,
#     level_1_code,
#     level_2_code,
#     level_3_code
# ) FROM '/tmp/skillsHierarchy_padded.csv' CSV HEADER"
