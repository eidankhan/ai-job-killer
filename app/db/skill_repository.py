# app/db/repositories/skill_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.skill import Skill
from app.models.occupation_skill_relation import OccupationSkillRelation

async def get_skill_by_id(db: AsyncSession, skill_id: int) -> Skill | None:
    """
    Fetch a skill by its ID.
    """
    query = select(Skill).where(Skill.id == skill_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_skills_for_occupation(db: AsyncSession, occupation_id: int) -> list[Skill]:
    """
    Fetch all skills linked to a given occupation.
    """
    query = (
        select(Skill)
        .join(OccupationSkillRelation, Skill.id == OccupationSkillRelation.skill_id)
        .where(OccupationSkillRelation.occupation_id == occupation_id)
    )
    result = await db.execute(query)
    return result.scalars().all()


async def list_skills(db: AsyncSession, limit: int = 100, offset: int = 0) -> list[Skill]:
    """
    Return a paginated list of skills.
    """
    query = select(Skill).limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()
