# OWASP ZAP Security Scan

This document describes how to run an OWASP ZAP baseline scan against the project gateway and how to interpret the results.

## Overview

- **Tool**: OWASP ZAP (Zed Attack Proxy) baseline scan
- **Target**: Gateway (e.g. `http://host.docker.internal:8080` when running locally with Docker)
- **Scan type**: Passive baseline (no authentication; limited crawl)

## How to Run

### Prerequisites

- Docker
- Gateway (and optionally backend services) running and reachable, e.g.:
  - Gateway on port 8080
  - Use `host.docker.internal` from inside the ZAP container to reach the host

### Command

From a directory where you want the report written (e.g. `docker/` or project root):

```bash
docker run -v $(pwd):/zap/wrk:rw \
  -t ghcr.io/zaproxy/zaproxy:stable zap-baseline.py \
  -t http://host.docker.internal:8080 \
  -r zap-report.html
```

- **`-t`**: Target URL (gateway base URL).
- **`-r`**: Report file name (written under the mounted volume, e.g. `./zap-report.html`).

Open the report:

```bash
open zap-report.html
```

### Optional: Custom policy or more URLs

- To scan more than the default crawl, use ZAP’s full scan or provide a list of URLs.
- API endpoints often require authentication; ZAP baseline does not log in, so only public routes (e.g. `/`, `/health`, `/metrics`) may be discovered. That’s expected and indicates protected API behavior.

## Latest Scan Summary (reference)

| Result | Count |
|--------|--------|
| **PASS** | 65 |
| **FAIL** | 0 |
| **WARN-NEW** | 2 |
| **WARN-INPROG** | 0 |

**Conclusion**: No failures. Gateway is clean from ZAP baseline’s perspective. The two warnings are minor and explained below.

## Findings

### Passed checks (65)

ZAP baseline ran its default passive rules (e.g. headers, cookies, content type, disclosure, crypto). All 65 checks that were applicable **passed** for the scanned URLs. No vulnerabilities were reported.

### Warnings (2)

#### 1. Storable and Cacheable Content [10049]

- **What it means**: Responses may be stored or cached by browsers/intermediaries.
- **Where**: Reported on:
  - `http://host.docker.internal:8080` (404)
  - `http://host.docker.internal:8080/robots.txt` (404)
  - `http://host.docker.internal:8080/sitemap.xml` (404)
- **Why it’s minor**: The gateway has no root handler and does not serve `robots.txt` or `sitemap.xml`; those URLs correctly return 404. The “storable/cacheable” warning on 404s is not a security issue for this API gateway.
- **Action**: No change required. If you add a root or static routes later, set appropriate `Cache-Control` (and other headers) per your security-audit and caching policy.

#### 2. Cross-Domain Misconfiguration [10098]

- **What it means**: CORS or cross-domain configuration might be permissive.
- **Where**: Reported on root and `robots.txt` (both 404).
- **Why it’s minor**: For local/dev, CORS is often configured with a broad origin (e.g. `*` or multiple origins). ZAP only saw a few URLs and no real API responses; the warning is generic.
- **Action**: Confirm CORS in code (e.g. gateway `constants.CORSAllowOrigin` or equivalent). Use restrictive origins and credentials settings in production; `*` in dev is acceptable for a personal project. See also [Security Architecture Audit](design-docs/security-audit.md).

## Why only 3 URLs?

ZAP baseline uses a simple crawl and does not authenticate. The gateway:

- Returns 404 for `/`, `/robots.txt`, `/sitemap.xml` (no root or static files).
- Exposes API routes that require authentication.

So ZAP only had 3 URLs to assess. That reflects correct behavior: unauthenticated callers do not see protected API content. Deeper coverage would require:

- A ZAP full scan with authentication (e.g. script or API token), or
- A URL list of public endpoints (e.g. `/health`, `/metrics`) if you want them explicitly included in the report.

## References

- [OWASP ZAP](https://www.zaproxy.org/)
- [ZAP Docker](https://www.zaproxy.org/docs/docker/)
- Project [Security Architecture Audit](design-docs/security-audit.md)
