"""Privacy-preserving, in-memory rate limiter.

Clients are tracked only by one-way salted HMAC digests, so raw IPs and device
tokens are never stored.
"""

import hashlib
import hmac
import secrets
import time
from typing import Dict, List

from fastapi import Request

from .config import (
    CLIENT_IP_HEADER,
    DAILY_LIMIT,
    MAX_RATE_LIMIT_KEYS,
    MAX_WINDOW_SECONDS,
    RATE_LIMIT_TIERS,
    TRUST_PROXY,
)

# Maps one-way salted HMAC digest -> chronologically ordered list of unix timestamps
rate_limit_db: Dict[str, List[float]] = {}
EPHEMERAL_RATE_SALT = secrets.token_bytes(32)


def _hash_identifier(namespace: str, raw_value: str) -> str:
    """Create a non-reversible ephemeral HMAC-SHA256 digest so raw IPs/fingerprints are never stored."""
    msg = f"{namespace}:{raw_value}".encode("utf-8")
    return hmac.new(EPHEMERAL_RATE_SALT, msg, hashlib.sha256).hexdigest()


def get_client_keys(request: Request) -> List[str]:
    """Return ephemeral hashed keys for both client IP and hardware/device token."""
    client_host = request.client.host if request.client else "unknown"
    raw_ip = client_host

    # Only trust proxy headers when TRUST_PROXY is explicitly enabled.
    # Order: operator-configured header (CLIENT_IP_HEADER) > X-Real-IP > rightmost X-Forwarded-For hop,
    # which prevents clients from spoofing their IP via a self-supplied X-Forwarded-For.
    if TRUST_PROXY:
        configured = (request.headers.get(CLIENT_IP_HEADER) or "").strip() if CLIENT_IP_HEADER else ""
        real_ip = (request.headers.get("x-real-ip") or "").strip()
        forwarded = (request.headers.get("x-forwarded-for") or "").strip()
        if configured:
            raw_ip = configured.split(",")[0].strip()
        elif real_ip:
            raw_ip = real_ip
        elif forwarded:
            raw_ip = forwarded.split(",")[-1].strip()

    keys = [_hash_identifier("ip", raw_ip)]

    device_token = (request.headers.get("x-device-token") or "").strip()
    if 16 <= len(device_token) <= 128:
        keys.append(_hash_identifier("dev", device_token))

    return keys


def prune_rate_limit_db(now: float) -> None:
    """Drop timestamps (and empty buckets) older than the longest window."""
    cutoff = now - MAX_WINDOW_SECONDS
    for k in list(rate_limit_db):
        fresh = [ts for ts in rate_limit_db[k] if ts > cutoff]
        if fresh:
            rate_limit_db[k] = fresh
        else:
            del rate_limit_db[k]


def _evaluate_timestamps_quota(ts_list: List[float], now: float) -> Dict[str, int]:
    """Evaluate 5/min, 20/day tiers for a single bucket of chronological timestamps."""
    min_remaining = DAILY_LIMIT
    max_reset_when_exhausted = 0

    for window_sec, max_links in RATE_LIMIT_TIERS:
        cutoff = now - window_sec
        window_ts = [ts for ts in ts_list if ts > cutoff]
        rem = max(0, max_links - len(window_ts))
        if rem < min_remaining:
            min_remaining = rem
        if rem == 0 and window_ts:
            boundary_ts = window_ts[-max_links] if len(window_ts) >= max_links else window_ts[0]
            tier_reset = max(1, int(window_sec - (now - boundary_ts)))
            if tier_reset > max_reset_when_exhausted:
                max_reset_when_exhausted = tier_reset

    return {
        "limit": DAILY_LIMIT,
        "used": len(ts_list),
        "remaining": min_remaining,
        "reset_in_seconds": max_reset_when_exhausted,
    }


def get_client_quota(
    request: Request,
    now: float | None = None,
    keys: List[str] | None = None,
    prune: bool = True,
) -> Dict[str, int]:
    """Evaluate quota across all anonymous client keys (IP hash + device hash) and return the strictest."""
    if now is None:
        now = time.time()
    if prune:
        prune_rate_limit_db(now)
    if keys is None:
        keys = get_client_keys(request)

    strictest = {
        "limit": DAILY_LIMIT,
        "used": 0,
        "remaining": DAILY_LIMIT,
        "reset_in_seconds": 0,
    }

    for key in keys:
        q = _evaluate_timestamps_quota(rate_limit_db.get(key, []), now)
        if q["remaining"] < strictest["remaining"] or (
            q["remaining"] == strictest["remaining"]
            and q["reset_in_seconds"] > strictest["reset_in_seconds"]
        ):
            strictest = q

    return strictest


def record_usage(keys: List[str], now: float) -> None:
    """Count one created secret against every client key, bounding total keys to prevent OOM."""
    for key in keys:
        if key not in rate_limit_db and len(rate_limit_db) >= MAX_RATE_LIMIT_KEYS:
            prune_rate_limit_db(now)
            if len(rate_limit_db) >= MAX_RATE_LIMIT_KEYS:
                oldest_key = next(iter(rate_limit_db), None)
                if oldest_key is not None:
                    rate_limit_db.pop(oldest_key, None)
        rate_limit_db.setdefault(key, []).append(now)
