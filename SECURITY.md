<div align="center">

<br />

<img src="public/tinhat.svg" alt="Tinhat logo" width="72" height="72" />

# Security Policy
### Ephemeral Confidentiality & Responsible Disclosure

Tinhat is built on a zero-persistence model: confidential secrets exist only in volatile RAM, burn immediately upon view, and leave zero forensic traces behind.

<br />

[![RAM Only](https://img.shields.io/badge/Storage-100%25%20In--Memory-%23f5c842?style=for-the-badge&labelColor=111326)](#-architectural-guarantees)
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

### 1. 🧠 Volatile RAM Only
* **No Persistent Storage**: Secrets exist strictly within process memory. They are never written to disk, SQLite/PostgreSQL databases, Redis, or container volumes.
* **Hardware-Level Purge**: If the process terminates, crashes, or the host restarts, all secrets are instantaneously lost at the memory controller level.

### 2. 🔥 Single-View Burn-on-Read
* **Atomic Deletion**: Decrypting a secret immediately executes an in-memory `pop()`.
* **Zero Window for Replay**: Once opened, subsequent requests to the same URL permanently return `404 Not Found`.

### 3. 🛡️ Blind Ephemeral Rate Limiting
* **No IP Storage**: IP addresses and client hardware identifiers are hashed using `HMAC-SHA256` with a high-entropy salt generated in memory upon server boot (`secrets.token_bytes(32)`).
* **Zero Traceability**: Raw client IPs are never recorded, logged, or correlated with any secret payload.
* **Automatic Eviction**: All rate limit timestamps older than 24 hours are automatically purged from RAM.

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
