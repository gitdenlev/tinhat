# ==============================================================================
# Multi-Stage Dockerfile for Tinhat (Svelte 5 + FastAPI)
# ==============================================================================

# ── Stage 1: Build Frontend ───────────────────────────────────────────────────
FROM node:22-alpine AS frontend-builder

WORKDIR /build

# Install dependencies first for optimal Docker layer caching
COPY package.json package-lock.json ./
RUN npm ci

# Copy sources and build production bundle
COPY vite.config.js index.html ./
COPY public/ ./public/
COPY src/ ./src/

RUN npm run build

# ── Stage 2: Production Runtime ───────────────────────────────────────────────
FROM python:3.13-slim AS production

# Security & runtime flags
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    HOST=0.0.0.0 \
    ENV=production

WORKDIR /app

# Install runtime dependencies (curl is used by container healthcheck)
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy built frontend assets from builder stage
COPY --from=frontend-builder /build/dist ./dist

# Copy static assets and backend application code
COPY public/ ./public/
COPY main.py ./
COPY backend/ ./backend/

# Security: Create non-root user (UID 1000) and drop root privileges
RUN groupadd -g 1000 appgroup && \
    useradd -u 1000 -g appgroup -s /bin/false appuser && \
    chown -R appuser:appgroup /app

USER appuser:appgroup

EXPOSE 8000

# Periodic health check to monitor app responsiveness
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Note: keep workers at 1 — rate-limit counters (and secrets, unless REDIS_URL is set) are in-memory
# Binds to $PORT so PaaS platforms (Render, Railway, Fly) that inject their own port just work.
CMD ["sh", "-c", "exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]

