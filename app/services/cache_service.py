import json
from datetime import timedelta
from app.core.redis import r

CACHE_EXPIRY = 60 * 60 * 24  # 24 hours in seconds

class CacheService:
    @staticmethod
    def _build_key(video_id: str, language: str) -> str:
        """Create a consistent cache key for transcripts."""
        return f"transcript:{video_id}:{language}"

    @staticmethod
    async def get_transcript(video_id: str, language: str) -> dict | None:
        """Retrieve transcript from Redis if it exists."""
        key = CacheService._build_key(video_id, language)
        data = await r.get(key)
        return json.loads(data) if data else None

    @staticmethod
    async def set_transcript(video_id: str, language: str, transcript_data: dict):
        """Save transcript in Redis with 24h TTL."""
        key = CacheService._build_key(video_id, language)
        await r.set(key, json.dumps(transcript_data), ex=CACHE_EXPIRY)
