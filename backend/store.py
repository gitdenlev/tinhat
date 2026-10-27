import json
import time
from typing import Any, Dict

from .config import CLEANUP_INTERVAL_SECONDS, REDIS_KEY_PREFIX, REDIS_URL
from .ratelimit import prune_rate_limit_db

SecretRecord = Dict[str, Any]


class StoreUnavailable(RuntimeError):
    """Raised when the storage backend cannot be reached."""


def _is_live(record: SecretRecord | None, now: float) -> bool:
    return bool(record) and now < record["expires_at"]


class MemoryStore:
    name = "memory"

    def __init__(self) -> None:
        self._db: Dict[str, SecretRecord] = {}

    def size(self) -> int:
        return len(self._db)

    def sweep(self, now: float) -> None:
        """Drop expired records (only this backend needs it; Redis uses TTL)."""
        for key in [k for k, v in self._db.items() if now >= v["expires_at"]]:
            self._db.pop(key, None)

    async def count(self) -> int:
        self.sweep(time.time())
        return len(self._db)

    async def put(self, secret_id: str, record: SecretRecord, ttl: int) -> None:
        self._db[secret_id] = record

    async def peek(self, secret_id: str) -> SecretRecord | None:
        record = self._db.get(secret_id)
        if record and not _is_live(record, time.time()):
            self._db.pop(secret_id, None)
            return None
        return record

    async def burn(self, secret_id: str) -> SecretRecord | None:
        record = self._db.pop(secret_id, None)
        return record if _is_live(record, time.time()) else None

    async def close(self) -> None:
        self._db.clear()


class RedisStore:
    """Redis/Upstash backend. One command per operation to stay within free quotas."""

    name = "redis"

    def __init__(self, url: str, prefix: str) -> None:
        import redis.asyncio as redis
        from redis.backoff import ExponentialBackoff
        from redis.exceptions import ConnectionError as RedisConnectionError
        from redis.exceptions import RedisError
        from redis.exceptions import TimeoutError as RedisTimeoutError
        from redis.retry import Retry

        self._errors = RedisError
        self._prefix = prefix
        # Upstash drops idle TCP connections; retrying on connection errors
        # transparently reconnects instead of failing the first request after idle.
        self._client = redis.from_url(
            url,
            decode_responses=True,
            socket_timeout=5,
            socket_connect_timeout=5,
            socket_keepalive=True,
            retry=Retry(ExponentialBackoff(cap=1.0, base=0.1), 3),
            retry_on_error=[RedisConnectionError, RedisTimeoutError],
        )

    def _key(self, secret_id: str) -> str:
        return f"{self._prefix}{secret_id}"

    async def _call(self, method: str, *args: Any, **kwargs: Any) -> Any:
        try:
            return await getattr(self._client, method)(*args, **kwargs)
        except self._errors as exc:
            raise StoreUnavailable("Secret storage is temporarily unavailable.") from exc

    @staticmethod
    def _decode(raw: str | None) -> SecretRecord | None:
        if not raw:
            return None
        record = json.loads(raw)
        return record if _is_live(record, time.time()) else None

    async def count(self) -> int:
        # DBSIZE counts every key in the logical DB: use a dedicated database.
        return int(await self._call("dbsize"))

    async def put(self, secret_id: str, record: SecretRecord, ttl: int) -> None:
        stored = await self._call("set", self._key(secret_id), json.dumps(record), ex=ttl, nx=True)
        if not stored:
            raise StoreUnavailable("Secret id collision, please retry.")

    async def peek(self, secret_id: str) -> SecretRecord | None:
        return self._decode(await self._call("get", self._key(secret_id)))

    async def burn(self, secret_id: str) -> SecretRecord | None:
        # GETDEL is atomic: two concurrent readers can never both get the secret.
        return self._decode(await self._call("getdel", self._key(secret_id)))

    async def close(self) -> None:
        await self._client.aclose()


def _build_store() -> MemoryStore | RedisStore:
    if REDIS_URL:
        return RedisStore(REDIS_URL, REDIS_KEY_PREFIX)
    return MemoryStore()


store = _build_store()
_last_cleanup_ts: float = 0.0


def cleanup_expired_secrets(now: float | None = None, force: bool = False) -> float:
    """Sweep expired in-memory secrets and stale rate-limit hashes. Never touches Redis.

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
    if isinstance(store, MemoryStore):
        store.sweep(now)
    prune_rate_limit_db(now)
    return now
