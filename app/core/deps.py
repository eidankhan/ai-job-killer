from fastapi import Depends, HTTPException, status, Request, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from datetime import datetime, timezone
from app.utils.security import decode_access_token
from app.core.redis import r  # your redis client
from time import time
from collections import defaultdict
from typing import Optional, Dict

# --- CONFIGURATION (from your original file) ---
DAILY_LIMIT = 3
DAY_SECONDS = 86400
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# --- 1. NEW CORE FUNCTION (Internal) ---
# This new function holds the shared logic for token decoding and revocation.
# We'll use this to build our other dependencies.
async def _get_payload_from_token(token: str) -> Optional[Dict]:
    """
    Internal core function:
    Tries to decode a token AND check for revocation.
    Returns payload (dict) on success, None on ANY failure.
    """
    try:
        payload = decode_access_token(token)
    except JWTError:
        # Invalid format or expired
        return None

    # ✅ Revocation check (from your original get_current_user)
    token_key = f"revoked:{payload['sub']}:{payload['iat']}"
    is_revoked = await r.get(token_key)
    if is_revoked:
        # Token is valid but has been revoked (e.g., by logout)
        return None

    # All checks passed, return the payload
    return payload


# --- 2. YOUR EXISTING FUNCTION (Refactored) ---
# This is now much simpler. It just handles the "required" part.
async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    """
    Dependency for protected endpoints.
    Requires a valid token and raises 401 on failure.
    
    (This is your original function, now refactored to be DRY)
    """
    payload = await _get_payload_from_token(token) # Reuse core logic

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid, expired, or revoked token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Returns the payload (dict) as your original function did
    return payload


# --- 3. NEW OPTIONAL AUTH FUNCTION ---
# This is the new dependency for our freemium endpoints.
async def get_optional_user(
    authorization: Optional[str] = Header(None),
) -> Optional[Dict]:
    """
    Dependency for public/freemium endpoints.
    Returns user payload (dict) if a valid token is provided, 
    None otherwise. Never raises a 401 error.
    """
    if not authorization:
        return None  # No auth header

    try:
        token_type, token = authorization.split()
        if token_type.lower() != "bearer":
            return None # Not a bearer token
    except ValueError:
        return None  # Malformed header
    
    # Reuse the same core logic!
    # If the token is invalid, expired, or revoked,
    # this will just return None, not raise an error.
    return await _get_payload_from_token(token)


# --- 4. YOUR RATE LIMITER (Refactored & Renamed) ---
# This is now "auth-aware". It uses get_optional_user.

async def get_rate_limiter(
    request: Request,
    user: Optional[Dict] = Depends(get_optional_user) # <-- THE KEY CHANGE
):
    """
    Applies a daily rate limit ONLY to guest users.
    Logged-in users are not limited.
    
    (This is your original daily_rate_limit, now refactored)
    """
    # If 'user' is not None, the user is logged in.
    if user:
        # We can even log their user ID
        logger.info(f"Rate limiter skipped for logged-in user: {user['sub']}")
        return  # <-- Skip all limits for authenticated users

    # --- If we get here, the user is a GUEST ---
    # (This is your original logic)
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
            status_code=4E+029, # Too Many Requests
            detail=f"Daily limit of {DAILY_LIMIT} requests reached. Try again in {ttl} seconds.",
            headers={"Retry-After": str(ttl)}
        )

    # Note: A pipeline is more efficient for multiple commands
    pipe = r.pipeline()
    pipe.incr(key, 1)
    pipe.expire(key, DAY_SECONDS, nx=True) # nx=True: only set
    await pipe.execute()