"""In-Memory Ephemeral Secret Store (nothing is ever written to disk)."""

import time
from typing import Any, Dict

from .config import CLEANUP_INTERVAL_SECONDS
from .ratelimit import prune_rate_limit_db

secrets_db: Dict[str, Dict[str, Any]] = {}
_last_cleanup_ts: float = 0.0


def cleanup_expired_secrets(now: float | None = None, force: bool = False) -> float:
    """Remove expired secrets and stale rate-limit hashes from the in-memory database.

    Full sweeps are throttled to once every CLEANUP_INTERVAL_SECONDS unless forced
    or an explicit timestamp is supplied, avoiding O(N) scans on every request.
    """
    global _last_cleanup_ts
    explicit_now = now is not None
    if now is None:
        now = time.time()

    if not force and not explicit_now and (now - _last_cleanup_ts) < CLEANUP_INTERVAL_SECONDS:
        return now

    _last_cleanup_ts = now
    expired_keys = [k for k, v in secrets_db.items() if now >= v["expires_at"]]
    for k in expired_keys:
        secrets_db.pop(k, None)
    prune_rate_limit_db(now)
    return now

    return now