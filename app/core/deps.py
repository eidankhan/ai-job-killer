from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from datetime import datetime, timezone
from app.utils.security import decode_access_token
from app.core.redis import r  # your redis client
from time import time
from collections import defaultdict
from time import time

DAILY_LIMIT = 3
DAY_SECONDS = 86400

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Extract current user from JWT, also check if token is revoked.
    """
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # ✅ Revocation check
    token_key = f"revoked:{payload['sub']}:{payload['iat']}"
    is_revoked = await r.get(token_key)
    if is_revoked:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload

async def daily_rate_limit(request: Request):
    anon_id = request.headers.get("X-Anonymous-Id", "").strip()
    fingerprint = request.headers.get("X-Fingerprint", "").strip()

    if not anon_id and not fingerprint:
        raise HTTPException(status_code=400, detail="Missing anonymous identification headers.")

    identifier = f"{anon_id}:{fingerprint}" if fingerprint else anon_id
    key = f"quota:{identifier}"

    count = await r.get(key)
    if count and int(count) >= DAILY_LIMIT:
        ttl = await r.ttl(key)
        raise HTTPException(
            status_code=429,
            detail=f"Daily limit of {DAILY_LIMIT} requests reached. Try again in {ttl} seconds.",
            headers={"Retry-After": str(ttl)}
        )

    pipe = r.pipeline()
    pipe.incr(key, 1)
    pipe.expire(key, DAY_SECONDS)
    await pipe.execute()

