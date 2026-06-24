# Security Exceptions

This document tracks vulnerabilities that the dep-audit scanner reports
but which cannot be remediated by upgrading the dependency at the
moment. Every exception must include:

- **CVE / advisory ID** — the scanner-reported identifier.
- **Package + version** — the version we're currently pinned to.
- **Severity** — vendor-assigned.
- **Why no fix is possible right now** — concrete reason.
- **Attack-surface impact analysis** — what an attacker can do in our
  deployment context (NOT the abstract CVE description).
- **Tracker link** — issue / PR / vendor advisory where progress is
  tracked.
- **Sunset condition** — the exact change that unblocks the upgrade,
  which removes the exception.

Pip-audit ignores: pass these IDs to `pip-audit --ignore-vuln <ID>` in
the CI workflow.
Yarn audit ignores: add `resolutions` entries in `package.json` instead
of `audit-ci`-style ignores where possible; document any audit-ci
ignores here.

---

## Active exceptions

### LITELLM-CVE-2026-35029, 35030, 42271, 47101, 47102, 49468, GHSA-69x8-hrgq-fjj8 (7 CVEs on `litellm==1.80.0`)

**Package + version**: `litellm==1.80.0`
**Severity**: mixed (LOW–HIGH; see individual advisories on GitHub).
**Why no fix is possible right now**:
- The package `emergentintegrations==0.2.0` (Emergent's internal LLM
  integration library, installed from the private CloudFront index
  `https://d33sy5i8bnduwe.cloudfront.net/simple/`) ships with two hard
  pins that block upgrading litellm:
  1. `openai==1.99.9` (strict pin in the wheel METADATA).
  2. `litellm @ https://customer-assets.emergentagent.com/internal-asset/library/litellm-1.80.0-py3-none-any.whl`
     (URL-pinned to a custom 1.80.0 wheel with looser sibling pins —
     `aiohttp>=3.10`, `openai>=1.99.5`).
- Every litellm version newer than 1.80.0 on PyPI requires either
  `openai>=2.8.0` or `openai==2.24.0` (depending on the litellm minor
  version) — both incompatible with the `openai==1.99.9` pin.
- We cannot upgrade `openai` without breaking `emergentintegrations`'s
  pin, and we cannot replace `litellm` without losing the
  Emergent-managed LLM key path (the primary mechanism for our
  customer-side LLM cost gating).

**Attack-surface impact analysis**:
- litellm is invoked SERVER-SIDE only, inside the SyniSense Shield
  pipeline (`get_synisense().shield_invoke(...)`).
- All input to litellm is already PII-stripped by Presidio + regex +
  spaCy NER before the LLM call (Shield deidentify pass).
- The litellm-reported CVEs are predominantly about request-handling
  surface that an attacker would need to control to exploit. In our
  deployment, the only LLM provider URL is configured server-side via
  environment variables; clients do not influence the URL or the
  request format.
- Net: the practical exploitability in our deployment is low for all 7
  CVEs, but they remain real CVEs and must not be "silently dismissed".

**Tracker link**: internal — Emergent platform team is the upstream
maintainer of `emergentintegrations`. Filing tracked at the
private internal repo.

**Sunset condition**: when Emergent publishes a version of
`emergentintegrations` (`0.3.0+`) that EITHER (a) relaxes the
`openai==1.99.9` strict pin to `openai>=1.99.5` (allowing openai 2.x)
OR (b) bumps its bundled `litellm` wheel to ≥1.83.14 (which fixes
all 7 CVEs at the litellm side).

**CI ignore flags** (when ready to switch from lenient pip-audit warnings
to a strict gate):
```
pip-audit -r backend/requirements.txt --strict \
  --ignore-vuln CVE-2026-35029 \
  --ignore-vuln CVE-2026-35030 \
  --ignore-vuln CVE-2026-42271 \
  --ignore-vuln CVE-2026-47101 \
  --ignore-vuln CVE-2026-47102 \
  --ignore-vuln CVE-2026-49468 \
  --ignore-vuln GHSA-69x8-hrgq-fjj8
```

---

## Sunsetted exceptions

(none yet — this section catalogues exceptions that have been removed
after a fix landed, with the commit that removed them, so we have an
audit trail of "we used to allow X but no longer do".)

---

## Maintenance rule

- Re-review every entry in this file MONTHLY (CI-scheduled `dep-audit`
  cron is the trigger).
- An exception older than 90 days requires a written re-justification.
- An exception older than 180 days triggers an escalation to the
  upstream owner (Emergent platform team for the litellm cluster
  above).
