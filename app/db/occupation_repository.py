# app/db/repositories/occupation_repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.occupation import Occupation

async def get_occupation_by_id(db: AsyncSession, occupation_id: int) -> Occupation | None:
    """
    Fetch an occupation by its ID.
    """
    query = select(Occupation).where(Occupation.id == occupation_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_occupation_by_label(db: AsyncSession, label: str) -> Occupation | None:
    """
    Fetch an occupation by its preferred label.
    """
    query = select(Occupation).where(Occupation.preferredLabel.ilike(f"%{label}%"))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def list_occupations(db: AsyncSession, limit: int = 100, offset: int = 0):
    """
    Return a paginated list of occupations.
    """
    query = select(Occupation).limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()
