"""JSON API routes."""

import re
import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, Response, status

from ..config import E2EE_PREFIX, MAX_ACTIVE_SECRETS, REQUIRE_E2EE, SECRET_ID_BYTES
from ..ratelimit import (
    ensure_client_cookie,
    get_client_keys,
    get_client_quota,
    record_usage,
)
from ..schemas import CreateSecretRequest
from ..store import MemoryStore, cleanup_expired_secrets, store

router = APIRouter()

# secrets.token_urlsafe(16) -> 22 URL-safe chars. Anything else cannot exist, so
# reject it without a storage round-trip (saves Redis commands on junk traffic).
_SECRET_ID_RE = re.compile(r"^[A-Za-z0-9_-]{16,64}$")


def _not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Secret not found or expired.",
    )


@router.get("/health", tags=["Health"])
@router.get("/api/health", tags=["Health"])
async def health_check():
    """Healthcheck endpoint (also used as keep-alive ping; never queries Redis)."""
    cleanup_expired_secrets()
    payload = {
        "status": "ok",
        "app": "Tinhat",
        "framework": "FastAPI + Svelte 5",
        "storage": store.name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    if isinstance(store, MemoryStore):
        payload["active_secrets"] = store.size()
    return payload


@router.get("/api/quota", tags=["Secrets"])
async def get_quota(request: Request, response: Response):
    """Get current secret generation quota for the client."""
    ensure_client_cookie(request, response)
    return get_client_quota(request)


@router.post("/api/secrets", tags=["Secrets"])
async def create_secret(req: CreateSecretRequest, request: Request, response: Response):
    """Create a new ephemeral text secret (5/min, 20/day per user)."""
    now = cleanup_expired_secrets()
    ensure_client_cookie(request, response)

    clean_text = req.text.strip()
    if not clean_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Secret message text cannot be empty.",
        )

    is_encrypted = clean_text.startswith(E2EE_PREFIX)
    if REQUIRE_E2EE and not is_encrypted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This server only accepts client-side encrypted (e2ee:v1) secrets.",
        )

    keys = get_client_keys(request)
    quota = get_client_quota(request, now=now, keys=keys, prune=False)
    if quota["remaining"] <= 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": "Quota for secret links reached. Please wait before generating more.",
                "quota": quota,
            },
        )

    if await store.count() >= MAX_ACTIVE_SECRETS:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Server secret capacity reached. Please try again shortly.",
        )

    secret_id = secrets.token_urlsafe(SECRET_ID_BYTES)
    expires_at = now + req.lifetime

    await store.put(
        secret_id,
        {
            "id": secret_id,
            "text": clean_text,
            "encrypted": is_encrypted,
            "lifetime": req.lifetime,
            "expires_at": expires_at,
        },
        ttl=req.lifetime,
    )

    # Count usage only once the secret is actually stored.
    record_usage(keys, now)
    updated_quota = get_client_quota(request, now=now, keys=keys, prune=False)

    return {
        "status": "ok",
        "id": secret_id,
        "encrypted": is_encrypted,
        "expires_at": expires_at,
        "lifetime": req.lifetime,
        "quota": updated_quota,
    }


@router.get("/api/secrets/{secret_id}", tags=["Secrets"])
async def get_secret_metadata(secret_id: str):
    """Get secret preview metadata prior to decryption."""
    now = cleanup_expired_secrets()
    if not _SECRET_ID_RE.match(secret_id):
        raise _not_found()

    secret = await store.peek(secret_id)
    if not secret:
        raise _not_found()

    return {
        "id": secret["id"],
        "encrypted": bool(secret.get("encrypted", False)),
        "timeout_seconds": max(0, int(secret["expires_at"] - now)),
        "lifetime": secret["lifetime"],
        "text_count": 1,
    }


@router.post("/api/secrets/{secret_id}/accept", tags=["Secrets"])
async def accept_secret(secret_id: str):
    """Decrypt & view secret once, then permanently delete it with zero trace."""
    cleanup_expired_secrets()
    if not _SECRET_ID_RE.match(secret_id):
        raise _not_found()

    secret = await store.burn(secret_id)
    if not secret:
        raise _not_found()

    return {
        "status": "ok",
        "text": secret["text"],
        "encrypted": bool(secret.get("encrypted", False)),
    }
