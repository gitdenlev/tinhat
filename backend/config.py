"""Paths, environment loading and tunable limits."""

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(BASE_DIR, "dist")
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
INDEX_HTML_PATH = os.path.join(DIST_DIR, "index.html")


def load_env_file(path: str | None = None) -> None:
    """Auto-load .env if present (existing environment variables always win)."""
    path = path or os.path.join(BASE_DIR, ".env")
    if not os.path.isfile(path):
        return
    with open(path, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("'\"")
            if key not in os.environ:
                os.environ[key] = value


# Must run before any setting below reads the environment.
load_env_file()

# ── Secrets & Cryptography ─────────────────────────────────────────────────
E2EE_PREFIX = "e2ee:v1:"
MAX_SECRET_LENGTH = 10000
MAX_ENCRYPTED_PAYLOAD_LENGTH = 60000
SECRET_ID_BYTES = 16  # 128 bits of entropy (OWASP recommendation)
MIN_LIFETIME = 10
MAX_LIFETIME = 86400
DEFAULT_LIFETIME = 3600

# ── Memory & DoS Protection Caps ───────────────────────────────────────────
MAX_ACTIVE_SECRETS = int(os.environ.get("MAX_ACTIVE_SECRETS", 2000))
MAX_RATE_LIMIT_KEYS = int(os.environ.get("MAX_RATE_LIMIT_KEYS", 50000))
CLEANUP_INTERVAL_SECONDS = 5.0

# ── Secret storage backend ─────────────────────────────────────────────────
# Empty REDIS_URL -> secrets live in process RAM (lost on restart / spin-down).
# Set it (e.g. Upstash "rediss://default:<password>@<host>.upstash.io:6379") to
# keep secrets across restarts, redeploys and free-tier sleep. Redis applies the
# TTL itself, so no sweeper is needed for that backend.
REDIS_URL = os.environ.get("REDIS_URL", "").strip()
REDIS_KEY_PREFIX = os.environ.get("REDIS_KEY_PREFIX", "tinhat:secret:").strip() or "tinhat:secret:"

# Reject non-E2EE (plaintext) payloads. Defaults to ON whenever an external
# store is configured, so a third-party provider only ever sees ciphertext; the
# decryption key stays in the URL #fragment and never reaches the server.
REQUIRE_E2EE = os.environ.get("REQUIRE_E2EE", "true" if REDIS_URL else "false").lower() in (
    "1",
    "true",
    "yes",
)

# ── Rate limiting ──────────────────────────────────────────────────────────
# Multi-tier rate limits: (window_seconds, max_links)
RATE_LIMIT_TIERS = (
    (60, 5),       # 5 links per minute
    (86400, 20),   # 20 links per 24 hours
)
MAX_WINDOW_SECONDS = max(window for window, _ in RATE_LIMIT_TIERS)
DAILY_LIMIT = max(limit for _, limit in RATE_LIMIT_TIERS)

# Anonymous client cookie used as a second rate-limit key. It contains only a
# random opaque value; clearing localStorage does not remove it. Clearing
# cookies still falls back to the IP key.
CLIENT_COOKIE_NAME = "tinhat_client"
CLIENT_COOKIE_MAX_AGE = MAX_WINDOW_SECONDS
# IPv6 subscribers usually control an entire /64, so rotate within it freely.
# Grouping by /64 prevents trivial address rotation from resetting the quota.
IPV6_CLIENT_PREFIX = 64

# ── Networking & CORS ──────────────────────────────────────────────────────
TRUST_PROXY = os.environ.get("TRUST_PROXY", "false").lower() in ("1", "true", "yes")
# Optional: name of a header set by YOUR trusted proxy that carries the real client IP
# (e.g. "true-client-ip" or "cf-connecting-ip"). Only read when TRUST_PROXY is enabled.
CLIENT_IP_HEADER = os.environ.get("CLIENT_IP_HEADER", "").strip().lower()
LOCAL_HOSTS = {"127.0.0.1", "::1", "localhost"}


def _build_cors_origins() -> list[str]:
    raw = os.environ.get("CORS_ORIGINS", "").strip()
    if raw:
        return [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]
    origins = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    site_url = os.environ.get("SITE_URL", "").strip().rstrip("/")
    if site_url and site_url not in origins:
        origins.append(site_url)
    return origins


CORS_ORIGINS = _build_cors_origins()

def _build_cors_origins() -> list[str]:
    raw = os.environ.get("CORS_ORIGINS", "").strip()
    if raw:
        return [o.strip().rstrip("/") for o in raw.split(",") if o.strip()]
    origins = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    site_url = os.environ.get("SITE_URL", "").strip().rstrip("/")
    if site_url and site_url not in origins:
        origins.append(site_url)
    return origins


CORS_ORIGINS = _build_cors_origins()

