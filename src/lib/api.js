const API_BASE = '/api';

const DAILY_SECRET_LIMIT = 20;
const DAILY_WINDOW_MS = 24 * 60 * 60 * 1000;
const RATE_LIMIT_TIERS_MS = [
  { windowMs: 60 * 1000, max: 5 },           // 5 links per minute
  { windowMs: DAILY_WINDOW_MS, max: 20 }     // 20 links per 24 hours
];
const QUOTA_STORAGE_KEY = 'tinhat_daily_quota_ts';

let cachedDeviceToken = null;

async function sha256Hex(input) {
  if (typeof crypto !== 'undefined' && crypto.subtle) {
    const data = new TextEncoder().encode(input);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    return Array.from(new Uint8Array(hashBuffer), (b) =>
      b.toString(16).padStart(2, '0')
    ).join('');
  }
  let h1 = 0xdeadbeef ^ input.length;
  let h2 = 0x41c6ce57 ^ input.length;
  for (let i = 0; i < input.length; i++) {
    const ch = input.charCodeAt(i);
    h1 = Math.imul(h1 ^ ch, 2654435761);
    h2 = Math.imul(h2 ^ ch, 1597334677);
  }
  h1 = Math.imul(h1 ^ (h1 >>> 16), 2246822507) ^ Math.imul(h2 ^ (h2 >>> 13), 3266489909);
  h2 = Math.imul(h2 ^ (h2 >>> 16), 2246822507) ^ Math.imul(h1 ^ (h1 >>> 13), 3266489909);
  return (h2 >>> 0).toString(16).padStart(8, '0') + (h1 >>> 0).toString(16).padStart(8, '0') + '00000000';
}

async function getDeviceToken() {
  if (cachedDeviceToken) return cachedDeviceToken;
  if (typeof window === 'undefined') return 'server';

  let gpuInfo = '';
  try {
    const canvas = document.createElement('canvas');
    const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
    if (gl) {
      const dbg = gl.getExtension('WEBGL_debug_renderer_info');
      const vendor = dbg ? gl.getParameter(dbg.UNMASKED_VENDOR_WEBGL) : gl.getParameter(gl.VENDOR);
      const renderer = dbg ? gl.getParameter(dbg.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER);
      gpuInfo = `${vendor || ''}|${renderer || ''}`;
    }
  } catch (_) {}

  const nav = typeof navigator !== 'undefined' ? navigator : {};
  const scr = typeof screen !== 'undefined' ? screen : {};
  const tz = typeof Intl !== 'undefined'
    ? Intl.DateTimeFormat().resolvedOptions().timeZone || ''
    : '';

  const rawSignals = [
    gpuInfo,
    `${scr.width || 0}x${scr.height || 0}x${scr.colorDepth || 0}`,
    `${window.devicePixelRatio || 1}`,
    `${nav.hardwareConcurrency || 0}`,
    `${nav.deviceMemory || 0}`,
    `${nav.maxTouchPoints || 0}`,
    `${nav.platform || ''}`,
    tz
  ].join('::');

  cachedDeviceToken = await sha256Hex(`tinhat-v1::${rawSignals}`);
  return cachedDeviceToken;
}

function readAndPruneTimestamps(now, appendNow = false) {
  let timestamps = [];
  if (typeof localStorage !== 'undefined') {
    try {
      const raw = localStorage.getItem(QUOTA_STORAGE_KEY);
      const parsed = raw ? JSON.parse(raw) : [];
      if (Array.isArray(parsed)) {
        timestamps = parsed.filter(
          (ts) => typeof ts === 'number' && now - ts < DAILY_WINDOW_MS
        );
      }
      if (appendNow) timestamps.push(now);
      localStorage.setItem(QUOTA_STORAGE_KEY, JSON.stringify(timestamps));
    } catch (_) {}
  }
  return timestamps;
}

function computeQuotaFromTimestamps(timestamps, now) {
  let minRemaining = DAILY_SECRET_LIMIT;
  let maxResetSeconds = 0;

  for (const tier of RATE_LIMIT_TIERS_MS) {
    const windowTs = timestamps.filter((ts) => now - ts < tier.windowMs);
    const rem = Math.max(0, tier.max - windowTs.length);
    if (rem < minRemaining) {
      minRemaining = rem;
    }
    if (rem === 0 && windowTs.length > 0) {
      const boundaryTs =
        windowTs.length >= tier.max
          ? windowTs[windowTs.length - tier.max]
          : windowTs[0];
      const resetSec = Math.max(
        1,
        Math.ceil((tier.windowMs - (now - boundaryTs)) / 1000)
      );
      if (resetSec > maxResetSeconds) {
        maxResetSeconds = resetSec;
      }
    }
  }

  return {
    limit: DAILY_SECRET_LIMIT,
    used: timestamps.length,
    remaining: minRemaining,
    reset_in_seconds: maxResetSeconds
  };
}

export function getLocalDailyQuota() {
  const now = Date.now();
  return computeQuotaFromTimestamps(readAndPruneTimestamps(now, false), now);
}

export function recordLocalSecretGeneration() {
  const now = Date.now();
  return computeQuotaFromTimestamps(readAndPruneTimestamps(now, true), now);
}

export function pickStricterQuota(serverQuota, localQuota) {
  if (
    typeof serverQuota?.remaining === 'number' &&
    (serverQuota.remaining < localQuota.remaining ||
      (serverQuota.remaining === localQuota.remaining &&
        (serverQuota.reset_in_seconds || 0) > localQuota.reset_in_seconds))
  ) {
    return serverQuota;
  }
  return localQuota;
}

export async function fetchDailyQuota() {
  const localQuota = getLocalDailyQuota();
  try {
    const deviceToken = await getDeviceToken();
    const res = await fetch(`${API_BASE}/quota`, {
      headers: { 'X-Device-Token': deviceToken }
    });
    if (res.ok) {
      return pickStricterQuota(await res.json(), localQuota);
    }
  } catch (_) {}
  return localQuota;
}

export async function createSecret(data) {
  const deviceToken = await getDeviceToken();
  const res = await fetch(`${API_BASE}/secrets`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Device-Token': deviceToken
    },
    body: JSON.stringify(data)
  });
  if (!res.ok) {
    if (res.status === 502 || res.status === 503 || res.status === 504) {
      const err = new Error('Backend server is unreachable (502 Bad Gateway). Please make sure the FastAPI backend is running on port 8000.');
      err.status = res.status;
      throw err;
    }
    const errorData = await res.json().catch(() => ({}));
    const detail = errorData.detail;
    const message =
      (typeof detail === 'object' && detail?.message) ||
      (typeof detail === 'string' && detail) ||
      'Failed to create secret';
    const err = new Error(message);
    err.status = res.status;
    if (typeof detail === 'object' && detail?.quota) {
      err.quota = detail.quota;
    }
    throw err;
  }
  return res.json();
}

export async function getSecret(secretId) {
  const res = await fetch(`${API_BASE}/secrets/${encodeURIComponent(secretId)}`);
  if (!res.ok) {
    if (res.status === 502 || res.status === 503 || res.status === 504) {
      const err = new Error('Backend server is unreachable (502 Bad Gateway). Please make sure the FastAPI backend is running on port 8000.');
      err.status = res.status;
      throw err;
    }
    const errorData = await res.json().catch(() => ({}));
    const err = new Error(errorData.detail || 'Secret not found or expired');
    err.status = res.status;
    throw err;
  }
  return res.json();
}

export async function acceptSecret(secretId) {
  const res = await fetch(`${API_BASE}/secrets/${encodeURIComponent(secretId)}/accept`, {
    method: 'POST'
  });
  if (!res.ok) {
    if (res.status === 502 || res.status === 503 || res.status === 504) {
      const err = new Error('Backend server is unreachable (502 Bad Gateway). Please make sure the FastAPI backend is running on port 8000.');
      err.status = res.status;
      throw err;
    }
    const errorData = await res.json().catch(() => ({}));
    const err = new Error(errorData.detail || 'Failed to accept secret');
    err.status = res.status;
    throw err;
  }
  return res.json();
}
