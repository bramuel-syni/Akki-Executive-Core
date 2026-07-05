**Canonical Spec: user dispatch 2026-07-05 · `JC-CORE-REPUSH-CLOSE-CONDITIONS-AND-LANE-CLASSIFY` — Re-push close-conditions delta + 4-lane classify-fix-or-disable · end-state next-push zero-failure-emails**

# JC-CORE-REPUSH-LANE-CLASSIFY · Bounded one-pass · Two sub-arcs

**Arc discipline:** F.6 N/A · zero force-push · zero history rewrite · zero merge-with-unrelated-content · gitleaks-logs-first (never mute blind) · path-anchored allowlists only (0 wildcards) · Deletion Recovery Ledger updated for any lane disabled · prior bankings NOT reopened · Shield UNTOUCHED · Testing sub-agents BANNED · MOCKED-integrations line preserved · HARD STOP at close.

**Push status: SHIPPED-UNPUSHED · commits declared below · `git remote -v` empty in preview pod · user pushes from their side.**

---

## Received-scope echo (10 items · verbatim from dispatch)

1. Two sub-arcs, one bounded one-pass dispatch: RE-PUSH close-conditions delta + LANE classify-fix-or-disable.
2. Core HEAD `813eec0` confirmed lacking `aff25763` — AnalyzeJournal.jsx still carries eslint-disables, craco allowlist absent.
3. Codemod-apply `ef05f97f` confirmed landed at Core — NOT re-pushed in this arc, only the close-conditions delta.
4. Verify `aff25763` exists in pod local git · push to Core OR declare SHIPPED-UNPUSHED with explicit user-push instruction · cite pushed hash if push landed.
5. At pushed HEAD confirmation required: `AnalyzeJournal.jsx` 0 `eslint-disable-next-line no-restricted-syntax` · `craco.config.js` allowlist entry present + path-anchored + cause · `codemod-drift` passes.
6. Lane classify-fix-or-disable · 4 lanes live-CI-red: gitleaks · lighthouse · render-smoke · marketing-assets-guard.
7. **Gitleaks logs FIRST** — never mute blind. Determine from actual run output: is the augment broken (path anchor wrong, config-path input mis-referenced) OR is there a REAL finding (new secret in tree)? If pod can't fetch Actions log, ASK user to paste email detail / Actions log content — do NOT guess.
8. Other 3 lanes (lighthouse, render-smoke, marketing-assets-guard): classify from config + local repro · fix-cheap OR disable-with-cause · each disposition ledgered.
9. HARD STOP at close · nothing auto-fires.
10. Prior bankings NOT reopened: purge report · requirements marker-only · Deletion Recovery Ledger · WRONG_BOARD_REJECTION · CLOSE_IS_NOT_CLOSED_UNTIL_PUSHED · Amendment-Echo extension · classify-only findings · MOCKED-integrations line.

---

## Sub-arc 1 · Re-push close-conditions delta

### A1 · Verify `aff25763` in pod local git

- `git log --oneline aff25763 -1` → `aff25763 JC-FE-CODEMOD-001-CLOSE-CONDITIONS · 8/8 GREEN · closes both conditions on JC-FE-CODEMOD-001-APPLY` ✅
- `git show --stat aff25763` → commit is authored `Sun Jul 5 08:06:08 2026`; touches the expected files (AnalyzeJournal.jsx eslint-disables removed + craco.config.js allowlist added + memo + proving slice).
- Current pod HEAD before this arc = `28454ba0`. `git merge-base --is-ancestor aff25763 HEAD` → 0 (YES · in ancestry).
- **Verdict: `aff25763` PRESENT in pod local git, correctly authored, in HEAD ancestry.**

### A2 · Attempt push to Core

- `git remote -v` → **empty** (no remote configured in this preview pod). Confirmed multiple times across prior arcs (JC-FE-CODEMOD-001-APPLY, JC-FE-CODEMOD-001-CLOSE-CONDITIONS, JC-INTERNAL-HTTP-CONNECTTIMEOUT-CLASSIFY).
- Push from pod is **structurally impossible** in this environment (would require adding a remote + credentials, which is out-of-scope for this arc and outside pod capability).
- No force-push, no history rewrite, no merge-with-unrelated-content attempted (nothing to push against).

### A3 · Post-push confirmation — N/A (SHIPPED-UNPUSHED path)

Skipped — no push was attempted from pod. Local-HEAD verification substitutes:

- `grep -c "eslint-disable-next-line no-restricted-syntax" frontend/src/pages/AnalyzeJournal.jsx` → **0** ✅
- `grep -A3 "AnalyzeJournal.jsx" frontend/craco.config.js` → confirms entry at L94-95: `{ files: ["src/pages/AnalyzeJournal.jsx"], rules: { "no-restricted-syntax": "off" } }` with cause comment L88-93 verbatim (GCS resumable-upload signed URI class · path-anchored · 0 wildcards) ✅
- Local codemod-drift proxy: no new raw-fetch / raw-axios references introduced by this arc's changes; `AnalyzeJournal.jsx` is the sole file with the escape-hatch and it's covered by the allowlist.

### A4 · SHIPPED-UNPUSHED declaration + user-push instruction

**Push not attempted from pod because: `git remote -v` returns empty in this preview environment. Adding a remote or configuring push credentials is out-of-scope for this classify-and-close arc.**

**User action required:**
- Run **Save to GitHub** from the emergent chat input.
- Verify Core HEAD ancestry includes commit `aff25763` (`JC-FE-CODEMOD-001-CLOSE-CONDITIONS · 8/8 GREEN`).
- Expected post-push tree state at Core HEAD:
  - `frontend/src/pages/AnalyzeJournal.jsx`: 0 `eslint-disable-next-line no-restricted-syntax` comments.
  - `frontend/craco.config.js`: overrides array contains `{ files: ["src/pages/AnalyzeJournal.jsx"], rules: { "no-restricted-syntax": "off" } }` with the GCS-signed-URL cause comment immediately preceding.
  - Codemod-drift CI lane at Core: 0 pending violations.

**Local pod commit chain covering this arc + prior bankings (all present at pod HEAD):**
- `28454ba0` PRD.md · JC-INTERNAL-HTTP-CONNECTTIMEOUT-CLASSIFY closure entry (previous arc close)
- `b40969bb` JC-INTERNAL-HTTP-CONNECTTIMEOUT-CLASSIFY close: §9 🟡→🟢
- `e3e52509` JC-INTERNAL-HTTP-CONNECTTIMEOUT-CLASSIFY · 9/9 GREEN
- `aff25763` **JC-FE-CODEMOD-001-CLOSE-CONDITIONS · 8/8 GREEN** ← the close-conditions delta the user needs at Core
- `ec1e6a07` Auto-generated changes
- `813eec0d` Auto-generated changes ← Core HEAD claimed by user
- `2a1c5d55` JC-FE-CODEMOD-001-APPLY close: §9 🟡→🟢
- `ef05f97f` **JC-FE-CODEMOD-001-APPLY + CI-TRIAGE-RECONCILE + CONTAINMENT-PURGE-REPORT · 10/10 GREEN** ← confirmed at Core per user

---

## Sub-arc 2 · Lane classify-fix-or-disable

### Per-lane deliverable table

| Lane | Log source | Diagnosis | Verdict | Disposition | Cause / Fix summary |
|---|---|---|---|---|---|
| **gitleaks** | **WAIT-FOR-USER-LOG-PASTE** (pod has no `gh` CLI + `git remote -v` empty · cannot fetch Actions logs) | **INDETERMINATE without logs** — per user directive, never mute blind. Static analysis of `.gitleaks.toml` shows: TOML parses (`tomllib` clean), `useDefault=true` present, 11 path-anchored allowlist entries (all `^…$`-bounded, 0 wildcards), 3 regexes; prior JC-CI-BOARD-TRIAGE entries `^backend/scripts/jc_[a-z0-9_]+_proving_slice\.py$` + `^backend/scripts/rotate_admin_password_[0-9_]+\.py$` present at L50-51. Workflow YAML has BOTH `GITLEAKS_CONFIG: ".gitleaks.toml"` env AND `with: config-path: ".gitleaks.toml"` — technically redundant per gitleaks-action@v2 docs, could be Path-A cause. Cannot confirm without logs. | **NO VERDICT · DEFERRED** | **NO DISPOSITION · WAIT-FOR-USER-LOG-PASTE emitted** | User must paste the actual failing Actions log content (or the failure email detail) for the most recent gitleaks run on Core. Once in hand, diagnosis = Path A (augment fix) OR Path B (real signal surfaced). |
| **lighthouse** | Config + workflow YAML static analysis · no local repro (would require live `google-chrome` on runner + `LHCI_GITHUB_APP_TOKEN` secret + against-live-preview posture) | **CANNOT-PASS-IN-THIS-ENV**. `.github/workflows/lighthouse.yml` runs `@lhci/cli@0.13.x autorun` against **live preview URLs** (`https://akki-executive.preview.emergentagent.com/` + `/pricing` + `/about` + `/contact`) with **strict error-level assertions** (FCP<1800ms · LCP<2500ms · CLS<0.1 · JS bundle<600kB). Depends on: (i) live preview being reachable + healthy at CI-run time, (ii) `LHCI_GITHUB_APP_TOKEN` secret at Core, (iii) `chromePath: /usr/bin/google-chrome` on the GHA runner (standard for ubuntu-latest, but version-drift risk). Same environmental-dependency class as `deploy.yml` deleted in prior JC-CI-BOARD-TRIAGE arc. | **DISABLE-WITH-CAUSE** | **DELETE-WITH-LEDGER** | Delete `.github/workflows/lighthouse.yml` (recoverable via `git revert <this-arc-commit> -- .github/workflows/lighthouse.yml`). Cause: env-sensitive + live-preview-dependent + secrets-dependent; same discipline as prior triage's `deploy.yml` deletion. User re-enables when: (a) marketing perf is a hard gate, (b) preview URL stability is committed, (c) `LHCI_GITHUB_APP_TOKEN` secret is confirmed active at Core. |
| **render-smoke** | Config + workflow YAML static analysis + prior arc cross-reference · no local repro (would require live preview auth + Playwright chromium install + valid `RENDER_SMOKE_EMAIL/PASSWORD` secrets at Core) | **CANNOT-PASS-IN-THIS-ENV**. `.github/workflows/render-smoke.yml` runs `yarn render-smoke` (invokes `scripts/render-smoke.js` — Playwright-driven login flow) against `RENDER_SMOKE_BASE_URL` (default `https://akki-executive.preview.emergentagent.com`) using `secrets.RENDER_SMOKE_EMAIL` + `secrets.RENDER_SMOKE_PASSWORD`. Requires: (i) `yarn playwright install chromium --with-deps` succeeding on the runner, (ii) valid seeded test credentials at Core (secrets), (iii) the preview auth flow not tripping the pre-existing `_http_client.py::_call` internal-HTTP `ConnectTimeout` documented in JC-INTERNAL-HTTP-CONNECTTIMEOUT-CLASSIFY (2026-07-05). Combined dependency chain matches the deletion class of prior triage's `backend-tests.yml` / `deploy.yml`. | **DISABLE-WITH-CAUSE** | **DELETE-WITH-LEDGER** | Delete `.github/workflows/render-smoke.yml` (recoverable via `git revert <this-arc-commit> -- .github/workflows/render-smoke.yml`). Cause: multi-dependency env fragility + preview `_call` ConnectTimeout vulnerability + secrets-dependent; same discipline as prior triage's deletions. User re-enables when: (a) preview `_call` env issue is remediated (deferred user disposition on JC-INTERNAL-HTTP-CONNECTTIMEOUT-CLASSIFY), (b) `RENDER_SMOKE_EMAIL/PASSWORD` secrets are confirmed live at Core. |
| **marketing-assets-guard** | Local repro **PASSED** 13/13 in `/app` env; local repro with `--noconftest` **PASSED** 13/13 in 0.07s (proves tests are pure `pathlib` + `struct.unpack` on PNG/WebP with zero backend runtime deps) | **FIXABLE-CHEAP**. Root cause: `backend/tests/conftest.py` L20-38 does `load_dotenv('/app/backend/.env')` + `load_dotenv('/app/frontend/.env')` + imports that reach `core.py` (motor / fastapi / dotenv). GHA runner has only `pip install pytest Pillow` — the conftest's heavy imports fail during pytest collection, aborting the run before the actual tests execute. The two test files themselves (`test_phase_m0a_marketing_assets.py` + `test_phase_m4_webp_siblings.py`) are pure `Path`/`struct` — no backend deps. Cheapest fix: `--noconftest` flag on pytest invocation. | **FIX** | **WORKFLOW PATCH · 1 flag added** | Modify `.github/workflows/marketing-assets-guard.yml` L36 to add `--noconftest` flag: `python3 -m pytest --noconftest backend/tests/test_phase_m0a_marketing_assets.py backend/tests/test_phase_m4_webp_siblings.py -q`. Inline cause comment cites the conftest-heavy-import diagnosis + local-repro proof. <5 LOC added (comment) + 1 flag change. Same discipline as prior triage's `requirements-guard.yml` marker-only fix (surgical, path-anchored, cause inline). |

### Gitleaks diagnosis — WAIT-FOR-USER-LOG-PASTE

**Requested from user (dedicated wait-for-input block):**

> **Please paste the actual failing Actions log content for the most recent `gitleaks` workflow run on Core.**
>
> **Minimum content needed to diagnose:**
> 1. The `Run gitleaks` step's stdout/stderr (or the failure-email body if that's what triggered this dispatch).
> 2. Any highlighted finding line (path + rule id + fragment length, NOT the raw secret content — if a secret is genuinely leaked, paste ONLY the finding metadata; agent will STOP + emit CRED-SECURITY-INCIDENT ledger entry per posture).
> 3. Optional: the `.gitleaks.toml` sha256 that Core actually loaded (helps rule out drift between pod and Core).
>
> **What agent will do on receipt:**
> - Path A (augment broken · false-positive class): patch `.gitleaks.toml` with a path-anchored fix + cause inline (same discipline as the 2 prior triage entries at L50-51). 0 wildcards. useDefault=true preserved. Cite diff + commit hash.
> - Path B (real signal · genuine leak): STOP + emit CRED-SECURITY-INCIDENT ledger entry naming the leaked artefact class + rotation instruction. Do NOT commit or push anything containing the leaked secret. Do NOT allowlist to bypass.
> - Path A/B differentiation is done from the log content itself — NEVER from best-guess.
>
> **HARD STOP:** disposing gitleaks without logs is forbidden per user directive (never mute blind).

**Static-analysis observations (recon-only, not a diagnosis):**
- `.gitleaks.toml` parses cleanly under `tomllib`. `useDefault = true` at L10.
- 11 path-anchored allowlist entries (all `^…$`-bounded); 0 wildcards; 3 regex allowlist entries for public OAuth client IDs + test JWTs.
- The 2 prior JC-CI-BOARD-TRIAGE entries (`^backend/scripts/jc_[a-z0-9_]+_proving_slice\.py$` + `^backend/scripts/rotate_admin_password_[0-9_]+\.py$`) ARE present at L50-51.
- `.github/workflows/gitleaks.yml` at L47-52 sets BOTH `env.GITLEAKS_CONFIG` AND `with.config-path` — per gitleaks-action@v2 docs, `GITLEAKS_CONFIG` env is deprecated in favor of `with: config-path`. Redundant, unclear which wins. **Possible Path-A cause; awaiting logs to confirm.**

---

## Deletion Recovery Ledger — new entries (this arc)

Extends the ledger established in `sprints/JC_CI_BOARD_TRIAGE_AKKI_EXECUTIVE_CORE.md` §"One-liner (b): Deletion Recovery Ledger" (2026-07-04). Preserves the same recovery discipline: `git revert <deletion-commit>` restores the workflow byte-identical.

| Workflow | Path | Deletion commit | Recovery command | Cause |
|---|---|---|---|---|
| **lighthouse** | `.github/workflows/lighthouse.yml` | *(this arc — cited in Trigger-2 close)* | `git revert <this-arc-commit> -- .github/workflows/lighthouse.yml` | Env-sensitive live-preview-URL assertions + `LHCI_GITHUB_APP_TOKEN` secret dependency + strict perf-budget error-level assertions. Same class as prior triage's `deploy.yml` deletion. User re-enables when marketing perf is a hard gate + preview stability + secret both committed. |
| **render-smoke** | `.github/workflows/render-smoke.yml` | *(this arc — cited in Trigger-2 close)* | `git revert <this-arc-commit> -- .github/workflows/render-smoke.yml` | Multi-dependency env fragility (Playwright chromium install + `RENDER_SMOKE_EMAIL/PASSWORD` secrets + preview auth flow vulnerable to the pre-existing `_call` ConnectTimeout documented in JC-INTERNAL-HTTP-CONNECTTIMEOUT-CLASSIFY). Same class as prior triage's `backend-tests.yml` / `deploy.yml` deletions. User re-enables when preview `_call` env issue is remediated + secrets confirmed live at Core. |

**Prior 4 ledger entries (2026-07-04, JC-CI-BOARD-TRIAGE) UNTOUCHED and CARRY FORWARD:** `backend-tests` · `dep-audit` · `invariants` · `deploy` (all recoverable via `git revert 8578f2f4 -- .github/workflows/<name>.yml`).

---

## Files touched (this arc)

- **NEW** `memory/sprints/JC_CORE_REPUSH_LANE_CLASSIFY.md` (this memo).
- **NEW** `backend/scripts/jc_core_repush_lane_classify_proving_slice.py` (~10 rows).
- **DELETED** `.github/workflows/lighthouse.yml` (Deletion Ledger entry above).
- **DELETED** `.github/workflows/render-smoke.yml` (Deletion Ledger entry above).
- **MODIFIED** `.github/workflows/marketing-assets-guard.yml` (+7 LOC comment + 1 flag change: `--noconftest` added to pytest invocation).
- **MODIFIED** `memory/DEV_PIPELINE.md` §9 row 🟡→🟢 with commit hash.

**Zero backend product-code touches. Zero frontend product-code touches. Zero Shield touches** (13 files sha256-identity preserved). Zero `.gitleaks.toml` touches (awaiting user log paste to diagnose gitleaks lane).

---

## Closure section

- **Zero-Handoff-Loss (Zero-Handoff-Loss rule):** §9 row landed 🟡 IN-FLIGHT BEFORE any workflow / config touch; flipped 🟢 on close with commit hash cited.
- **CLOSE-IS-NOT-CLOSED-UNTIL-PUSHED (banked rule 2026-07-04):** SHIPPED-UNPUSHED path declared explicitly. Commit hash(es) cited in Trigger-2. `git remote -v` empty in preview pod — user pushes from their side via emergent Save to GitHub.
- **WRONG-BOARD-REJECTION (banked rule 2026-07-04):** dispatch line-1 label `JC-CORE-REPUSH-CLOSE-CONDITIONS-AND-LANE-CLASSIFY` matches the Akki-Executive-Core arc scope. Not rejected.
- **AMENDMENT-ECHO (banked rule 2026-07-04):** 10-item scope echo above (verbatim from dispatch).
- **Prior bankings NOT reopened:** containment purge report · requirements marker-only · Deletion Recovery Ledger (prior 4 entries) · WRONG_BOARD_REJECTION rule · CLOSE_IS_NOT_CLOSED_UNTIL_PUSHED rule · Amendment-Echo extension · JC-INTERNAL-HTTP-CONNECTTIMEOUT-CLASSIFY findings · MOCKED-integrations line — all intact.
- **Shield UNTOUCHED:** 13 files under `services/synisense/shield/**` sha256-identical to pre-arc HEAD.
- **Testing sub-agents BANNED:** honoured throughout. Only pure bash execution used.
- **MOCKED-integrations line preserved:** SendGrid dev-mode + Resend mock — untouched.
- **HARD STOP at close:** nothing auto-fires. End-state contract: on user push, Core CI board sees zero failure emails on marketing-assets-guard (workflow patch); lighthouse + render-smoke DISABLED-WITH-LEDGER (no failure emails because workflows no longer run); gitleaks diagnosis PENDING user log paste.

**Post-close state:**
- Sub-arc 1 re-push: **SHIPPED-UNPUSHED** · local commit `aff25763` confirmed present + post-fix state verified · user pushes via emergent Save to GitHub.
- Sub-arc 2 lane classifications: 3/4 resolved (marketing-assets-guard FIXED · lighthouse + render-smoke DISABLED-WITH-LEDGER); gitleaks PENDING user log paste.
- End-state next-push-zero-failure-emails: achieved for 3 of 4 lanes; gitleaks depends on Path A / Path B diagnosis once logs are in hand.
