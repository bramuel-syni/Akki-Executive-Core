# Phase 5.3 — Dep-Audit Remediation + Codemod Institutionalisation

**Dispatch:** Phase 5.3 — Build Dispatch (dep-audit remediation + codemod rail).
**Status:** ✅ **SHIPPED** — both parts; CVE count cut from 53 → 7 on pip side and from 29 HIGH+ → 0 HIGH/CRITICAL on yarn side; 7 remaining pip findings documented in `SECURITY_EXCEPTIONS.md` (all blocked on Emergent platform upstream).
**Iteration budget:** 1/3 used.

---

## 1. Honest scope snapshot

Per the dispatch's Phase 5.2 size-honesty rail, this dispatch was sized
honestly:

| Part | Stated scope | Actual scope |
|---|---|---|
| A — pip-audit findings | unstated | **53 vulns / 10 pkgs**; 46 fixed, 7 documented exceptions |
| A — yarn-audit findings | unstated | **74 vulns total / 29 HIGH+**; all HIGH+ resolved via `resolutions` + 1 direct bump |
| B — codemod institutionalisation | doc + 3+ candidates | 1 codemod moved into structured tree + 4 candidates seeded |

No scope explosion. The actual scope was within single-iteration capacity.

---

## 2. Dep-audit baseline (pre-fix scanner output)

### pip-audit (backend)

Baseline run: `cd /app/backend && pip-audit -r requirements.txt --format json`
→ exit 1, **53 vulnerabilities across 10 packages**:

| Package | Pinned | CVE count | Highest fix needed |
|---|---|---|---|
| `aiohttp` | 3.13.5 | 11 | 3.14.1 |
| `urllib3` | 2.6.3 | 3 | 2.7.0 |
| `cryptography` | 46.0.7 | 1 | 48.0.1 |
| `starlette` | 0.37.2 | 8 | 1.3.1 (gated on FastAPI ≥0.135) |
| `idna` | 3.11 | 1 | 3.15 |
| `litellm` | 1.80.0 | 7 | 1.83.14 (gated on emergentintegrations openai pin) |
| `pymongo` | 4.5.0 | 1 | 4.6.3 |
| `pyjwt` | 2.12.1 | 8 | 2.13.0 |
| `pypdf` | 6.10.2 | 8 | 6.13.3 |
| `python-multipart` | 0.0.24 | 5 | 0.0.31 |

### yarn audit (frontend)

Baseline run: `cd /app/frontend && yarn audit --groups dependencies --level high`
→ exit ≥1, **74 vulnerabilities** (18 low + 27 moderate + 27 high + 2 critical).
HIGH+CRITICAL breakdown:

| Package | Source | Patched-in |
|---|---|---|
| `axios` (direct) | direct | ≥1.16.0 |
| `@babel/plugin-transform-modules-systemjs` | react-scripts > | ≥7.29.4 |
| `fast-uri` | react-scripts > webpack > ajv > | ≥3.1.2 |
| `form-data` | react-scripts > jest > jsdom > AND axios > | ≥3.0.5 / ≥4.0.6 |
| `nth-check` | react-scripts > | ≥2.0.1 |
| `react-router` | react-router-dom > | ≥7.15.0 |
| `serialize-javascript` | react-scripts > workbox > | ≥7.0.3 |
| `shell-quote` | react-scripts > | ≥1.8.4 |
| `underscore` | react-scripts > bfj > jsonpath > | ≥1.13.8 |
| `ws` | react-scripts > jest > jsdom > AND react-scripts > webpack-dev-server > | ≥7.5.11 / ≥8.21.0 |

---

## 3. Per-finding remediation table

### pip side

| Package | Old → New | Action | Verified |
|---|---|---|---|
| `aiohttp` | 3.13.5 → **3.14.1** | direct bump in `requirements.txt` | ✅ 11 CVEs gone |
| `urllib3` | 2.6.3 → **2.7.0** | direct bump | ✅ 3 CVEs gone |
| `cryptography` | 46.0.7 → **48.0.1** | direct bump | ✅ 1 CVE gone |
| `starlette` | 0.37.2 → **1.3.1** | direct bump (required fastapi co-bump) | ✅ 8 CVEs gone |
| `idna` | 3.11 → **3.15** | direct bump | ✅ 1 CVE gone |
| `pymongo` | 4.5.0 → **4.6.3** | direct bump | ✅ 1 CVE gone |
| `pyjwt` | 2.12.1 → **2.13.0** | direct bump | ✅ 8 CVEs gone |
| `pypdf` | 6.10.2 → **6.13.3** | direct bump | ✅ 8 CVEs gone |
| `python-multipart` | 0.0.24 → **0.0.31** | direct bump | ✅ 5 CVEs gone |
| `fastapi` | 0.110.1 → **0.138.0** | co-bump (starlette range gate) | ✅ healthy on boot |
| `litellm` | 1.80.0 → **(unchanged)** | exception logged; blocked on emergentintegrations | ⚠️ 7 CVEs documented |

**Why litellm stuck at 1.80.0**:
- `emergentintegrations 0.2.0` (Emergent's private internal LLM lib)
  ships a strict `openai==1.99.9` pin + a URL-pin to a custom
  `litellm-1.80.0` wheel.
- Every litellm >1.80.0 on PyPI requires `openai>=2.8.0` or
  `openai==2.24.0` — both incompatible with the Emergent pin.
- Replacing litellm would break the Emergent-managed LLM key path
  (primary mechanism for customer-side LLM cost gating).
- Full impact analysis in `/app/backend/SECURITY_EXCEPTIONS.md`.

### yarn side

| Package | Source | Action |
|---|---|---|
| `axios` | direct dep | bumped `dependencies.axios` from `^1.8.4` to **`^1.16.0`** in `package.json` |
| `@babel/plugin-transform-modules-systemjs` | transitive | `resolutions: ">=7.29.4"` (capped at `~7.29.4` for Node 20 compat) |
| `fast-uri` | transitive | `resolutions: ">=3.1.2"` |
| `form-data` | transitive | `resolutions: ">=4.0.6"` (covers both 3.0.5 + 4.0.6 patch paths) |
| `nth-check` | transitive | `resolutions: ">=2.0.1"` |
| `react-router` | transitive (via react-router-dom) | `resolutions: ">=7.15.0"` (capped at `~7.15.0` for Node 20 compat; 8.x requires Node ≥22.22) |
| `serialize-javascript` | transitive | `resolutions: ">=7.0.3"` |
| `shell-quote` | transitive | `resolutions: ">=1.8.4"` |
| `underscore` | transitive | `resolutions: ">=1.13.8"` |
| `ws` | transitive | `resolutions: ">=8.21.0"` |

**Why two cap-downs (`~7.29.4`, `~7.15.0`)**:
- `@babel/plugin-transform-modules-systemjs@8.x` requires Node ≥22 or
  ≥24; the GHA runner / supervisor pod is on Node 20.
- `react-router@8.x` requires Node ≥22.22.
- `7.29.x` (babel) and `7.15.x` (react-router) are the latest CVE-fixed
  releases that still support Node 20. Both will need re-bumping when
  the Node base image upgrades.

---

## 4. Post-fix scanner runs (clean exit evidence)

### pip-audit

```
$ cd /app/backend && pip-audit -r requirements.txt
Found 7 known vulnerabilities in 1 package
  litellm 1.80.0  CVE-2026-35029  ...
  litellm 1.80.0  CVE-2026-35030  ...
  litellm 1.80.0  CVE-2026-42271  ...
  litellm 1.80.0  CVE-2026-47101  ...
  litellm 1.80.0  CVE-2026-47102  ...
  litellm 1.80.0  CVE-2026-49468  ...
  litellm 1.80.0  GHSA-69x8-hrgq-fjj8  ...
EXIT 1
```

Exit 1 is expected with the lenient GHA workflow currently in place
(emits warnings, doesn't fail). The 7 remaining are documented in
`SECURITY_EXCEPTIONS.md` with the explicit `--ignore-vuln` invocation
the workflow can adopt when flipping to `--strict`:

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

### yarn audit

```
$ cd /app/frontend && yarn audit --groups dependencies --level high
yarn audit v1.22.22
40 vulnerabilities found - Packages audited: 1613
Severity: 16 Low | 24 Moderate
Done in 1.05s.
EXIT 0
```

**EXIT 0** at the configured `--level high` threshold (the GHA gate).
The 16 low + 24 moderate findings are below the threshold and are not
job-failing.

---

## 5. Sprint contract verification

### Wire-level zero behaviour change
- All public path counts preserved: synisense=40, solva=62, akki=595.
- OpenAPI sha pins held: tested via the canonical Phase 4.4 dual-mount
  smoke (`tests/test_phase4_4_dual_mount_smoke.py`) → **37/37 PASS**.
- SDK slice files refreshed to track FastAPI 0.138.0's internal
  serialization metadata (slice byte content changed by ~156 bytes
  per slice; **public path content unchanged**). `scripts/generate_sdk_slices.py`
  was run; the SDK slices invariant `test_invariant_sdk_slices.py`
  PASSES post-regen.

### Invariant suite — full sweep
- `pytest tests/invariants/ tests/test_phase4_4_dual_mount_smoke.py tests/test_phase4_2_http_transport_smoke.py -q`
  → **94 PASS, 10 docs-skip, 0 fail** (49.22s).
- All six named ratchet/smoke tests in the dispatch spec PASS:
  - `tests/invariants/test_invariant_no_raw_axios.py` → 2/2 PASS
  - `tests/invariants/test_invariant_polymorphic_response_ratchet.py` → 3/3 PASS
  - `tests/invariants/test_invariant_deploy_smoke_present.py` → 6/6 PASS
  - `tests/test_phase4_4_dual_mount_smoke.py` → 37/37 PASS
  - `tests/test_phase4_2_http_transport_smoke.py` → 8/8 PASS

### FE tests
- `yarn test --testPathPattern="apiV2|validatedCall"` → **10/10 PASS** under axios 1.16.0.

### Smoke
- Public homepage (`/`) → renders cleanly. "Akki refuses to invent."
  hero visible, no JS console errors.
- `/api/healthz/composite` → HTTP 200, 3/3 contexts green.

---

## 6. Codemod pattern installation

### File tree
```
/app/scripts/codemods/
├── 001_raw_axios_to_apiv2.py    (moved from /app/scripts/)
└── README.md                     (new — 6-section codemod convention)
```

### README sections covered
1. **When to use a codemod** — N>50 + mechanical + pattern-expressible
   + non-destructive + verifiable.
2. **Idempotency rule** — second run must be a no-op; verified for
   codemod 001 (apply 155 → re-run 0).
3. **Naming convention** — `NNN_short_description.py`, monotonic.
4. **Required structure** — docstring + dry-run + apply + count line.
5. **Verification rule** — every codemod ships a build-breaking
   invariant test; codemod 001 → `test_invariant_no_raw_axios.py`.
6. **Non-destructive convention** — no reformat, no delete, no
   touching `_archived/` or build outputs.

### Candidate Future Codemods seeded
Four concrete candidates with scope, pattern, pre-reqs, and verification
locks:

1. **`NNN_dict_any_to_pydantic_model.py`** (Phase 5.4) — 49 `Optional[Dict[str, Any]]` routes; AST-match + mapping table.
2. **`NNN_print_to_logger_info.py`** (only if applicable) — verify scope first; might be skipped if grep is sparse.
3. **`NNN_archived_dead_code_removal.py`** — delete `_archived/` and shrink codemod 001's whitelist.
4. **`NNN_emergent_envvar_to_typed_settings.py`** (Phase 6) — `os.environ.get("AKKI_*")` → typed `BaseSettings`.

### Cross-references updated
- `backend/tests/invariants/test_invariant_no_raw_axios.py` — 3
  references to old path `scripts/codemod_raw_axios_to_apiv2.py`
  updated to new path `scripts/codemods/001_raw_axios_to_apiv2.py`.
- Memo references in MASTER_STATE.md + the Phase 5.2 memo are
  historical pointers; updated only if practical, but the file move
  is one-way (the old path no longer exists).

### Idempotency re-verification post-move
```
$ python /app/scripts/codemods/001_raw_axios_to_apiv2.py
[APPLIED] 0 files; 0 import-line rewrites.
```
Re-running the codemod from its new home is a no-op. ✅

---

## 7. MASTER_STATE.md diff

Section 4 Track A — Phase 5.3 entry appended after Phase 5.2:
- Two-part deliverable summary (A dep remediation + B codemod rail).
- Pre→post scanner counts: 53 → 7 (pip), 29 HIGH+ → 0 HIGH (yarn).
- Files-touched inventory.
- Verification evidence (94/94 invariants + ratchet + 10/10 FE tests).
- 4-item deviations log.
- Iteration budget 1/3.

Section 9 (or footer) — single sentence pointing to
`/app/scripts/codemods/README.md` as the codemod convention.

---

## 8. Sprint memo pointer

This memo lives at
`/app/memory/sprints/PHASE_5_3_DEP_AUDIT_AND_CODEMOD.md`.

Related artefacts:
- `/app/backend/SECURITY_EXCEPTIONS.md` — the 7 litellm CVEs + sunset
  conditions.
- `/app/scripts/codemods/README.md` — codemod convention rail.

---

## 9. Deviations log

| # | Deviation | Rationale |
|---|---|---|
| D1 | 7 litellm CVEs remain (vs A.5 "documented in SECURITY_EXCEPTIONS.md") | Exactly the documented-exception path the dispatch allows. Blocked on `emergentintegrations` upstream — Emergent platform team owns the unblock. Sunset condition captured. |
| D2 | aiohttp pin in `requirements.txt` shows 3.14.1 while the installed wheel was 3.14.1 from the `aiohttp>=3.10` looser pin in the Emergent-built `litellm-1.80.0` wheel | The Emergent custom litellm wheel relaxes upstream litellm's exact `aiohttp==3.13.4` pin to `aiohttp>=3.10`. This is what allows the aiohttp 3.14.1 bump despite the litellm freeze. Documented in `SECURITY_EXCEPTIONS.md`. |
| D3 | OpenAPI slice byte content drifted ~156 B per slice after FastAPI 0.110 → 0.138 bump | FastAPI's internal OpenAPI serialization changed (more `description` defaults, minor schema metadata tweaks). Public PATH content unchanged — verified by 37/37 dual-mount smoke. Slices were regenerated via the existing `scripts/generate_sdk_slices.py`; ratchet hash UNCHANGED. |
| D4 | `@babel/plugin-transform-modules-systemjs` and `react-router` capped at the latest Node 20-compatible minor (`~7.29.4` and `~7.15.0`) | The supervisor pod runs Node 20.20.2; the latest releases (`8.x` for both) require Node ≥22. Cap-downs are necessary; will need re-bumping when the base image upgrades. CVE fix versions are still satisfied (≥7.29.4 covers the babel CVE; ≥7.15.0 covers the react-router CVE). |
| D5 | `axios > form-data` had both `>=3.0.5` and `>=4.0.6` patched paths; used `>=4.0.6` in resolutions (covers both since they're separate semver lines) | yarn `resolutions` accepts a single version range per package; `>=4.0.6` is strictly stronger than `>=3.0.5` for the form-data 4.x line (used by axios), and the form-data 3.x line under react-scripts > jsdom resolves to the latest 4.x version under the same `>=4.0.6` resolution. Verified by `yarn audit` exit 0. |

---

## 10. Honest scope accounting

| Area | Expected | Actual | Notes |
|---|---|---|---|
| pip findings to fix | unstated | 46 (of 53 total — 87% remediation) | 7 documented unfixables blocked on upstream |
| yarn findings to fix | unstated | 29 HIGH+ → 0 HIGH+ (100% remediation at the GHA gate) | 40 lower-sev findings remain below `--level high` threshold |
| Direct deps bumped | unstated | 10 (`requirements.txt`) + 1 (`package.json`) | |
| Transitive resolutions added | unstated | 9 (yarn `resolutions` block, new) | |
| Slice regenerations | 0 expected | 1 (`scripts/generate_sdk_slices.py`) | Required by the FastAPI bump; no public surface change |
| Codemod migrations performed | 0 (move-only) | 0 + 1 idempotency re-verify | |
| New invariant tests written | 0 | 0 | Existing invariants verify the codemod move + pin changes |
| Deviation count | unbounded | 5 | All documented above |

**Iteration budget**: 1/3 used. Iter-2/3 reserved for follow-up if a
CI run surfaces a scanner finding this iteration missed, OR if a Node
base image upgrade unlocks the babel/react-router cap-down release.

---

## Pointer for the next agent

If picking up Phase 5.4 (polymorphic narrowing):
1. Author per-route Pydantic models in `contracts/responses.py`
   FIRST (one batch, ~10 routes).
2. Write the codemod: `/app/scripts/codemods/NNN_dict_any_to_pydantic_model.py`
   — AST-match the FastAPI decorator + a mapping table you author at
   the top.
3. Ship the diff harness alongside (per the dispatch's wire-byte rail).
4. After running the codemod, decrement
   `_BASELINE_POLY_ROUTE_COUNT` in
   `test_invariant_polymorphic_response_ratchet.py` by the batch size.
5. Cross off the candidate entry in
   `/app/scripts/codemods/README.md`'s "Candidate Future Codemods"
   list.

If a CI dep-audit re-fail surfaces:
1. Re-run scanners locally with the EXACT GHA flags (mirror the
   workflow invocation).
2. Compare against the baseline in this memo's §2.
3. If new finding: same flow as this dispatch (Inventory →
   Classify → Verify).
4. If old finding re-emerged: someone bumped a dep down or the
   resolutions block was edited; restore the lock.

If Emergent publishes `emergentintegrations 0.3.0+` with a looser
openai pin:
1. Bump `emergentintegrations` in `requirements.txt`.
2. Bump `openai` to `>=2.x`.
3. Bump `litellm` to ≥1.83.14.
4. Re-run pip-audit; the 7 litellm CVEs should clear.
5. Remove the active exception from `SECURITY_EXCEPTIONS.md` (move
   to the Sunsetted section with the commit hash).
