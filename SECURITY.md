<div align="center">

<br />

<img src="public/tinhat.svg" alt="Tinhat logo" width="72" height="72" />

# Security Policy
### Ephemeral Confidentiality & Responsible Disclosure

Tinhat is built on a zero-persistence model: confidential secrets exist only in volatile RAM, burn immediately upon view, and leave zero forensic traces behind.

<br />

[![Ephemeral Storage](https://img.shields.io/badge/Storage-Ephemeral%20(RAM%20%7C%20Redis%20TTL)-%23f5c842?style=for-the-badge&labelColor=111326)](#-architectural-guarantees)
[![Privacy](https://img.shields.io/badge/Privacy-Burn--on--Read-%23e05c5c?style=for-the-badge&labelColor=111326)](#-architectural-guarantees)
[![Zero Logs](https://img.shields.io/badge/Logs-Zero%20Logs-%237cf0c0?style=for-the-badge&labelColor=111326)](#-architectural-guarantees)

<br />

</div>

---

## 🛡️ Supported Versions

Only the current active release line receives security updates, vulnerability patches, and architectural audits:

| Version | Supported | Status |
| :--- | :---: | :--- |
| **2.x** *(Current)* | ✅ | Actively maintained with security fixes |
| **< 2.0** | ❌ | End of Life (no patches provided) |

---

## 🔐 Architectural Guarantees

> [!IMPORTANT]
> Tinhat operates under a strict **Zero-Persistence Guarantee**. The service is intentionally engineered so that data recovery is impossible once a secret has been accessed or its timer expires.

### 1. 🧠 Ephemeral Storage
* **In-Memory by Default**: Without `REDIS_URL`, secrets exist strictly within process memory and are never written to disk, databases or container volumes. If the process terminates, crashes, or the host restarts, all secrets are lost.
* **Optional Redis Backend**: With `REDIS_URL` set (e.g. Upstash), secrets are stored as Redis keys with a native TTL equal to their lifetime, so they survive restarts, redeploys and free-tier spin-downs.
* **Ciphertext Only in Redis**: In Redis mode `REQUIRE_E2EE` defaults to `true`, so the server rejects any payload that is not client-side encrypted (`e2ee:v1`). The decryption key lives only in the URL `#fragment` and never reaches the server or the storage provider.
* **Provider Caveat**: A managed Redis may persist data to disk/backups on its side. Deleted or expired keys are unreadable through the API immediately, but the provider's own retention of encrypted bytes is outside Tinhat's control.

### 2. 🔥 Single-View Burn-on-Read
* **Atomic Deletion**: Decrypting a secret immediately executes an in-memory `pop()` or an atomic Redis `GETDEL`, so two concurrent readers can never both receive it.
* **Zero Window for Replay**: Once opened, subsequent requests to the same URL permanently return `404 Not Found`.

### 3. 🛡️ Blind Ephemeral Rate Limiting
* **No IP Storage**: IP addresses and client hardware identifiers are hashed using `HMAC-SHA256` with a high-entropy salt generated in memory upon server boot (`secrets.token_bytes(32)`).
* **Server-Side Enforcement**: The quota is checked and recorded by the API, never by the browser. Clearing `localStorage` only removes a display hint; it does not reset the server bucket.
* **Anonymous Cookie + IP Keys**: A random first-party `HttpOnly` cookie (24h) provides a per-browser bucket, while the hashed IP (IPv6 grouped by `/64`) provides a fallback when cookies are cleared. Neither value is linked to a secret.
* **Zero Traceability**: Raw client IPs are never recorded, logged, or correlated with any secret payload.
* **Automatic Eviction**: All rate limit timestamps older than 24 hours are automatically purged from RAM.
* **Process-Local State**: Counters reset when the process restarts and are not shared between workers/replicas. For durable multi-instance enforcement, use a shared store such as Redis.

### 4. 🚫 Cache & Leak Prevention
* **Aggressive Headers**: Secret endpoints deliver `Cache-Control: no-store, no-cache, must-revalidate` and `Pragma: no-cache`.
* **Anti-Leakage**: `Referrer-Policy: no-referrer` prevents token leakage through third-party links or browser histories.
* **Search Engine Exclusion**: `X-Robots-Tag: noindex, nofollow, noarchive` explicitly forbids search engine crawlers from indexing secret URLs.

---

## 🚨 Reporting a Vulnerability

We treat potential security vulnerabilities with the highest priority. If you discover a security flaw, we ask that you practice responsible disclosure.

> [!CAUTION]
> **Please do not report security vulnerabilities via public GitHub issues, discussions, or pull requests.**

### How to Report Privately:
1. **GitHub Security Advisory**: Open a confidential report using GitHub's **[Private Vulnerability Reporting](https://github.com/gitdenlev/tinhat/security/advisories/new)** tab on this repository.
2. **Direct Contact**: If private reporting is unavailable, reach out directly to the repository maintainers.

### What to Include:
* Description of the vulnerability and attack vector.
* Clear steps to reproduce (including a proof-of-concept script or cURL commands where applicable).
* Assessment of potential exploit impact.
* Suggested mitigation or remediation, if known.

### Response Commitment:
* **Initial Acknowledgment**: Within **48 hours**.
* **Triage & Assessment**: Within **5 business days**.
* **Patch Release**: Coordinated fix deployed directly to the `main` branch.

---

<div align="center">

Crafted with care for privacy and digital confidentiality.

</div>
