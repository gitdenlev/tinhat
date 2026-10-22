"""JSON API routes."""

import secrets
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Request, status

from ..config import E2EE_PREFIX, MAX_ACTIVE_SECRETS, SECRET_ID_BYTES
from ..ratelimit import get_client_keys, get_client_quota, record_usage
from ..schemas import CreateSecretRequest
from ..store import cleanup_expired_secrets, secrets_db

router = APIRouter()


@router.get("/health", tags=["Health"])
@router.get("/api/health", tags=["Health"])
async def health_check():
    """Healthcheck endpoint."""
    cleanup_expired_secrets()
    return {
        "status": "ok",
        "app": "Tinhat",
        "framework": "FastAPI + Svelte 5",
        "active_secrets": len(secrets_db),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/api/quota", tags=["Secrets"])
async def get_quota(request: Request):
    """Get current secret generation quota for the client."""
    return get_client_quota(request)


@router.post("/api/secrets", tags=["Secrets"])
async def create_secret(req: CreateSecretRequest, request: Request):
    """Create a new ephemeral text secret (5/min, 20/day per user)."""
    now = cleanup_expired_secrets()
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

    if len(secrets_db) >= MAX_ACTIVE_SECRETS:
        now = cleanup_expired_secrets(force=True)
        if len(secrets_db) >= MAX_ACTIVE_SECRETS:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Server secret capacity reached. Please try again shortly.",
            )

    clean_text = req.text.strip()
    if not clean_text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Secret message text cannot be empty.",
        )

    is_encrypted = clean_text.startswith(E2EE_PREFIX)
    secret_id = secrets.token_urlsafe(SECRET_ID_BYTES)
    expires_at = now + req.lifetime

    record_usage(keys, now)
    updated_quota = get_client_quota(request, now=now, keys=keys, prune=False)

    secrets_db[secret_id] = {
        "id": secret_id,
        "text": clean_text,
        "encrypted": is_encrypted,
        "lifetime": req.lifetime,
        "expires_at": expires_at,
    }

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

    secret = secrets_db.get(secret_id)
    if secret and now >= secret["expires_at"]:
        secrets_db.pop(secret_id, None)
        secret = None

    if not secret:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Secret not found or expired.",
        )

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
    now = cleanup_expired_secrets()

    secret = secrets_db.pop(secret_id, None)
    if not secret or now >= secret["expires_at"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Secret not found or expired.",
        )

    return {
        "status": "ok",
        "text": secret["text"],
        "encrypted": bool(secret.get("encrypted", False)),
    }
