# Phase AUDIT_P1 — CI Lane Greens

**Date:** 2026-06-24
**Status:** CLOSED — three product-code-free commits shipped locally; pipeline-log-sync re-verified GREEN.
**Type:** CI policy/config polish following the AUDIT_P0 close-out. Strict report-only on vuln lanes; allowlist-extension on the two POLICY-RED lanes; no product code touched.
**Source dispatch:** User dispatch "RETRY — Repo is public again. Re-verify and execute P1.".

## Headline result

Three product-code-free commits, all GREEN:

| Sub-item | Commit | Result |
|---|---|---|
| **P1.1** — commit `frontend/yarn.lock` | `8b6b7fc7` | `yarn install --frozen-lockfile` deterministic on CI |
| **P1.2** — pip-audit verification (report-only) | (no commit) | 0 REAL findings under existing IGNORED_VULNS env |
| **P1.3** — annotate spaCy github-release lines | `9a3c6c97` | requirements-guard exit `1 → 0`; self-test 8 passed / 1 legacy-skipped |
| **P1.4** — yarn audit verification (report-only) | (no commit) | 0 HIGH/CRITICAL under `--level high` (1 613 deps; 16 Low + 24 Moderate below threshold) |
| **P1.5** — extend `.gitleaks.toml` allowlist | `f944f365` | full-history `gitleaks detect` `5 findings → 0 findings` |

No STOP conditions tripped. No product code touched. No remote pushes. No dependency version bumps.

## Step 1 — Pre-flight Branch Verification (post-deletion)

After the user deleted the 10 dirty dependabot branches manually on GitHub and toggled the repo back to public, fresh fetch + per-branch contamination scan:

```
$ git fetch --all --prune
From https://github.com/bramuel-syni/Akki-Executive-New-Arch
 - [deleted]           (none)     -> origin/dependabot/npm_and_yarn/frontend/eslint-10.5.0
 - [deleted]           (none)     -> origin/dependabot/npm_and_yarn/frontend/minor-updates-88c466843a
 - [deleted]           (none)     -> origin/dependabot/npm_and_yarn/frontend/patch-updates-7e2e8046cf
 - [deleted]           (none)     -> origin/dependabot/npm_and_yarn/frontend/tailwindcss-4.3.1
 - [deleted]           (none)     -> origin/dependabot/npm_and_yarn/frontend/tiptap/react-3.27.1
 - [deleted]           (none)     -> origin/dependabot/pip/backend/bcrypt-5.0.0
 - [deleted]           (none)     -> origin/dependabot/pip/backend/patch-updates-1817b53aa3
 - [deleted]           (none)     -> origin/dependabot/pip/backend/thinc-9.1.1
 - [deleted]           (none)     -> origin/dependabot/pip/backend/weasyprint-69.0
 - [deleted]           (none)     -> origin/dependabot/pip/backend/minor-updates-5cd06ca4c1
```

10 dependabot branches deleted (the user deleted 9 in the first pass, then deleted PR #14 + its branch when surfaced in pre-flight). Final remote-tracking refs:

| Branch | HEAD | Tree | Log |
|---|---|---|---|
| `origin/main` | `9f51d335` | CLEAN_TREE | CLEAN_LOG |
| `origin/dependabot/github_actions/actions/checkout-7` | `45f92264` | CLEAN_TREE | CLEAN_LOG |
| `origin/dependabot/github_actions/actions/setup-python-6` | `760dabc9` | CLEAN_TREE | CLEAN_LOG |
| `origin/dependabot/github_actions/actions/upload-artifact-7` | `91d27668` | CLEAN_TREE | CLEAN_LOG |

**Verdict: CLEAN.** Every remaining remote branch passed `git ls-tree -r <branch> --name-only | grep -E '^backup/|\.bson$'` (empty) and `git log <branch> --full-history -- backup/ '*.bson'` (empty). Rolled straight into P1.

Pre-flight evidence-gap note: an intermediate attempt failed because the GitHub repo was momentarily private during the fork-resume window. User flipped it back to public; verification resumed. Stop-and-surface protocol held both times (Message 629 dirty-cache surfacing + Message 641 single-branch straggler surfacing).

## Step 2 — Per-Task Execution

### P1.1 — Commit `frontend/yarn.lock`

**Before:**
```
$ git status --short -- frontend/yarn.lock
?? frontend/yarn.lock
$ wc -l frontend/yarn.lock
14160 frontend/yarn.lock
$ git check-ignore -v frontend/yarn.lock
(exit 1 — not ignored; OK to commit)
```

**Action:**
```
$ cd frontend && yarn install
yarn install v1.22.22
[1/4] Resolving packages...
success Already up-to-date.
Done in 0.36s.

$ yarn install --frozen-lockfile
yarn install v1.22.22
[1/4] Resolving packages...
success Already up-to-date.
Done in 0.36s.

$ cd /app && git add frontend/yarn.lock
$ git commit -m "ci(P1.1): commit yarn.lock for deterministic installs"
[main 8b6b7fc7] ci(P1.1): commit yarn.lock for deterministic installs
 1 file changed, 14160 insertions(+)
 create mode 100644 frontend/yarn.lock
```

**After:**
```
$ git status --short -- frontend/yarn.lock
(empty — file is tracked and clean)
$ git log --oneline -1
8b6b7fc7 ci(P1.1): commit yarn.lock for deterministic installs
```

**Verdict:** GREEN. Lockfile committed; `yarn install --frozen-lockfile` passes locally, matches the `dep-audit.yml::npm-audit` step at line 102.

### P1.2 — pip-audit verification (report-only)

**Workflow gate** (`.github/workflows/dep-audit.yml:42-90`):
```
env:
  IGNORED_VULNS: "CVE-2026-35029,CVE-2026-35030,CVE-2026-42271,CVE-2026-47101,CVE-2026-47102,CVE-2026-49468,GHSA-69x8-hrgq-fjj8"
# ...
- name: Audit backend requirements (strict, with documented exceptions)
  run: |
    set +e
    pip-audit -r backend/requirements.txt --format json > audit.json
    set -e
    python3 - <<'PY'
    # ... triage block: ignore listed CVEs, fail on anything else
    PY
```

**Local execution under the same env:**
```
$ pip-audit -r backend/requirements.txt --format json > /tmp/p1_pipaudit.json
$ export IGNORED_VULNS="CVE-2026-35029,...,GHSA-69x8-hrgq-fjj8"
$ python3 <triage block from workflow>

pip-audit summary:
  total packages scanned: 192
  total vulns found:      7
  IGNORED via SECURITY_EXCEPTIONS: 7
    - litellm: CVE-2026-35029  (MITIGATED via IGNORED_VULNS env)
    - litellm: CVE-2026-35030  (MITIGATED via IGNORED_VULNS env)
    - litellm: GHSA-69x8-hrgq-fjj8  (MITIGATED via IGNORED_VULNS env)
    - litellm: CVE-2026-42271  (MITIGATED via IGNORED_VULNS env)
    - litellm: CVE-2026-49468  (MITIGATED via IGNORED_VULNS env)
    - litellm: CVE-2026-47102  (MITIGATED via IGNORED_VULNS env)
    - litellm: CVE-2026-47101  (MITIGATED via IGNORED_VULNS env)
  REAL/BLOCKING (unignored): 0

VERDICT: pip-audit GREEN under CI ignore-list (matches dep-audit.yml).
```

**Classification:** All 7 findings are in `litellm` — the Phase 5.4 exception cluster blocked on the `emergentintegrations` upstream `openai==1.99.9` pin. Full attack-surface analysis + sunset conditions in `backend/SECURITY_EXCEPTIONS.md`. All MITIGATED. **No REAL findings.** No requirements.txt changes. No §9 follow-up needed.

### P1.3 — Annotate spaCy github-release lines

**Before** (`backend/requirements.txt:33-36`):
```
emergentintegrations==0.1.0
en_core_web_lg @ https://github.com/explosion/spacy-models/releases/download/en_core_web_lg-3.8.0/en_core_web_lg-3.8.0-py3-none-any.whl#sha256=293e9547a655b25499198ab15a525b05b9407a75f10255e405e8c3854329ab63
en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl#sha256=1932429db727d4bff3deed6b34cfc05df17794f4a52eeb26cf8928f7c1a0fb85
et_xmlfile==2.0.0

$ python3 scripts/check_requirements_urls.py --root .
  ERR backend/requirements.txt:34:pep508-direct-ref  en_core_web_lg @ ...
  ERR backend/requirements.txt:35:pep508-direct-ref  en_core_web_sm @ ...
check_requirements_urls: FAILED — 2 offending line(s).
exit 1
```

**Action:** Per `scripts/check_requirements_urls.py:67` (`ALLOW_MARKER = "ci-requirements-guard: allow"`), append `# ci-requirements-guard: allow spacy-models-via-github-release` to both lines.

**After diff:**
```
diff --git a/backend/requirements.txt b/backend/requirements.txt
index 862ab49d..ca7e11dd 100644
--- a/backend/requirements.txt
+++ b/backend/requirements.txt
@@ -31,8 +31,8 @@ docstring_parser==0.18.0
 ecdsa==0.19.2
 email-validator==2.3.0
 emergentintegrations==0.1.0
-en_core_web_lg @ https://github.com/.../en_core_web_lg-3.8.0-py3-none-any.whl#sha256=293e9547...
-en_core_web_sm @ https://github.com/.../en_core_web_sm-3.8.0-py3-none-any.whl#sha256=1932429d...
+en_core_web_lg @ https://github.com/.../en_core_web_lg-3.8.0-py3-none-any.whl#sha256=293e9547...  # ci-requirements-guard: allow spacy-models-via-github-release
+en_core_web_sm @ https://github.com/.../en_core_web_sm-3.8.0-py3-none-any.whl#sha256=1932429d...  # ci-requirements-guard: allow spacy-models-via-github-release
 et_xmlfile==2.0.0
 fastapi==0.138.0
 fastuuid==0.14.0
```

**Verification:**
```
$ python3 scripts/check_requirements_urls.py --root .
  ok  backend/requirements.txt
check_requirements_urls: OK — 1 file(s) scanned, 0 offenses.
exit 0   (was 1)

$ python3 -m pytest backend/tests/test_requirements_guard.py -q
8 passed, 1 skipped, 21 warnings in 4.54s
```

The 1 skip is `tests/test_requirements_guard.py:120` — the Wave8 deliberate-skip on the spaCy/emergentintegrations URL-pin block. It was already there before P1; unchanged. Self-test infra confirms the guard correctly handles direct-URL refs both with and without the allow marker.

**Commit:** `9a3c6c97 ci(P1.3): annotate spaCy github-release lines for requirements-guard`.

### P1.4 — yarn audit verification (report-only)

**Workflow gate** (`.github/workflows/dep-audit.yml:92-117`):
```
- name: Audit (high or critical only)
  working-directory: frontend
  run: |
    set +e
    yarn audit --groups dependencies --level high
    status=$?
    set -e
    if [ $status -ge 1 ]; then
      echo "::error title=npm-audit::yarn audit reported HIGH/CRITICAL vulnerabilities (exit=$status)"
      exit $status
    fi
```

**Local execution (matching the workflow exactly):**
```
$ cd frontend && yarn audit --groups dependencies --level high
yarn audit v1.22.22
40 vulnerabilities found - Packages audited: 1613
Severity: 16 Low | 24 Moderate
Done in 1.01s.
exit 0
```

**Full-spectrum JSON breakdown (for transparency):**
```
auditSummary:
  vulnerabilities: {info:0, low:16, moderate:24, high:0, critical:0}
  dependencies:    1613
  devDependencies: 0
  optional:        0

HIGH/CRITICAL total: 0
```

**Verdict:** GREEN under CI threshold. 16 Low + 24 Moderate are below threshold (Dependabot's slow-burn channel per workflow comment at line 34). No commits. No §9 follow-up needed.

### P1.5 — Extend `.gitleaks.toml` allowlist

**Pre-state** (`gitleaks detect --no-banner --redact --config .gitleaks.toml`, 726 commits scanned, 18.6s):
```
total findings: 5
  - memory/audit/P0_ci_log_triage.md:21         ruleID=generic-api-key
  - memory/sprints/PHASE_AUDIT_P0.md:153        ruleID=generic-api-key
  - memory/sprints/P5_8_4_postmark_winddown.md:11  ruleID=generic-api-key
  - docs/PRODUCT_REVIEW.md:281                  ruleID=generic-api-key
  - docs/PRODUCT_REVIEW.md:375                  ruleID=generic-api-key
```

Findings 1-3 share one false-positive class: each line quotes the original `BASIC_AUTH_USER=zy7Yym3uHloLWWJT` from the Postmark wind-down memo (the 16-char USER name, not the secret — secret is in an adjacent column, redacted). Findings 4-5 share the second class: literal `<REDACTED_ROTATE_AFTER_LEAK>` placeholder text in the product-review audit-trail markdown.

**Honest-extension note re: dispatch scope:**
The dispatch specified two allowlist paths:
- `^memory/sprints/.*\.md$`
- `^docs/PRODUCT_REVIEW\.md$`

These cover 4 of 5 findings (`P5_8_4_postmark_winddown:11`, `PHASE_AUDIT_P0:153`, `PRODUCT_REVIEW:281`, `PRODUCT_REVIEW:375`). The fifth finding (`memory/audit/P0_ci_log_triage.md:21`) is in the `memory/audit/` directory — a new directory created during AUDIT_P0 itself, post-dating the P1.5 spec. Same false-positive class as `memory/sprints/`, same forensic-documentation use case. Added `^memory/audit/.*\.md$` as a third allowlist path under the same class. Explicit explanation in the commit message.

**Diff:**
```
diff --git a/.gitleaks.toml b/.gitleaks.toml
index 4627888c..f28bb784 100644
--- a/.gitleaks.toml
+++ b/.gitleaks.toml
@@ -31,6 +31,15 @@ paths = [
   '''^\.gitleaks\.toml$''',
   # frontend STORAGE_KEY constants — these are localStorage keys, not secrets.
   '''^frontend/src/components/cohort/Day16Banner\.jsx$''',
+  # AKKI Audit (P1.5, 2026-06-24) — sprint memos + audit memos quote
+  # redaction markers (`<REDACTED_ROTATE_AFTER_LEAK>`) and
+  # already-rotated basic-auth USER identifiers (`BASIC_AUTH_USER=...`,
+  # not the secret) for forensic completeness. These are
+  # documentation, not live credentials. Same allowlist class as the
+  # below per-path override for test_credentials.md.
+  '''^memory/sprints/.*\.md$''',
+  '''^memory/audit/.*\.md$''',
+  '''^docs/PRODUCT_REVIEW\.md$''',
 ]
```

**Post-state** (same command, same depth):
```
1:47PM INF 726 commits scanned.
1:47PM INF scan completed in 17.7s
1:47PM INF no leaks found

total findings: 0
```

**Commit:** `f944f365 ci(P1.5): extend gitleaks allowlist for sprint/audit memos and product review`.

## Maintenance Protocol Compliance

Per the standing rule (`DEV_PIPELINE.md` §1, §2, §4, §5, §9 updated BEFORE the sprint memo):

1. ✅ §1 Current State — AUDIT_P1 closure preamble added; AUDIT_P0 demoted to "(prior)" line.
2. ✅ §2 Active Dispatch — P2 (Correctness & Clarity) named as next.
3. ✅ §4 Invariant Ladder Snapshot — new CI-hygiene row added: "dep-audit-strict (pip + npm) + requirements-guard + gitleaks all provably GREEN under documented allowlists".
4. ✅ §5 Surface Ratchet unchanged (P1 didn't touch product code; no slice change).
5. ✅ §9 Phase History — AUDIT_P1 row added at the top with the 5-task summary + the three commit ids + the honest-extension note.
6. ✅ `pipeline-log-sync.yml` KNOWN_MAPPINGS already had `AUDIT_P1: AUDIT_P1` from P0's pre-emptive extension (line 216).
7. ✅ This memo file written AFTER §9 row exists, so pipeline-log-sync is satisfied.

## Final Verification (inline output)

**pipeline-log-sync** (the workflow's own algorithm, run inline against the current `memory/sprints/` + `memory/DEV_PIPELINE.md`):
```
pipeline-log-sync: OK. 101 retained sprint memo(s) checked: 33 have matching §9 rows, 68 are legacy-allowlisted (pre-2026-06-24 baseline).
exit 0
```

The 33 matched §9 rows include `AUDIT_P1` (matched to this memo via `KNOWN_MAPPINGS["AUDIT_P1"] = "AUDIT_P1"` at `.github/workflows/pipeline-log-sync.yml:216`).

**gitleaks (full-history, post-everything)**:
```
1:51PM INF 727 commits scanned.
1:51PM INF scan completed in 17.8s
1:51PM INF no leaks found
final findings: 0
exit 0
```

The new sprint memo + the DEV_PIPELINE.md updates do not regress gitleaks. Allowlist is correctly scoped.

## Files touched

### Modified
- `frontend/yarn.lock` — newly tracked (14 160 lines / 662 KB).
- `backend/requirements.txt` — 2 lines annotated with the allow-marker (lines 34 + 35; no version changes).
- `.gitleaks.toml` — 3 paths added to `[allowlist].paths` (sprints/ + audit/ + PRODUCT_REVIEW.md).
- `memory/DEV_PIPELINE.md` — §1 (current state), §2 (active dispatch), §4 (CI-hygiene row), §9 (AUDIT_P1 row).

### Created
- `memory/sprints/PHASE_AUDIT_P1.md` (this file).

### Untouched (deliberately)
- All product code — `backend/server.py`, `backend/routers/**`, `backend/services/**`, `frontend/src/**`.
- All dependency versions — `package.json`, `backend/requirements.txt` content (only the comment column changed).
- Remote — no `git push`, no `git push --delete`, no remote pushes of any kind. User will run `Save to GitHub` from the platform UI.

## What the user MUST do next

⚠️ **Remote push is up to the user.** This memo + the three P1 commits + the DEV_PIPELINE.md updates are local-only.

To push:
```
# Via the platform "Save to GitHub" flow (recommended), OR:
git push origin main
```

Three commits to land:
- `8b6b7fc7` ci(P1.1): commit yarn.lock for deterministic installs
- `9a3c6c97` ci(P1.3): annotate spaCy github-release lines for requirements-guard
- `f944f365` ci(P1.5): extend gitleaks allowlist for sprint/audit memos and product review
- Plus the DEV_PIPELINE.md + this memo (one final commit, see below).

After the push, the user should:
1. Confirm `dep-audit.yml::pip-audit` is GREEN on `main`.
2. Confirm `dep-audit.yml::npm-audit` is GREEN on `main`.
3. Confirm `requirements-guard.yml` is GREEN on `main`.
4. Confirm `gitleaks.yml` is GREEN on `main`.
5. Confirm `pipeline-log-sync.yml` is GREEN on `main` (this memo + DEV_PIPELINE.md §9 row are paired).

## Stop-and-report (none tripped)

- ❌ Any REAL pip-audit finding outside the IGNORED_VULNS list — none.
- ❌ Any HIGH/CRITICAL yarn-audit finding — none.
- ❌ Any gitleaks finding after the allowlist extension — none.
- ❌ Any product code change required — none.
- ❌ Any remote push attempt — none (local-only, per dispatch).

## Next

P2 (Correctness & Clarity) awaits user approval. P2 actionable surface per the audit close-out brief:
- Tenancy audit on `strategic_goal_evolution.py`; add `untenanted=True` invariant.
- Canonicalize Solva/Monitor `_v2` paths.
- Add `thinklab` UI-label-only invariant.

Then ThinkLab Gate A (render-check + Flag 3 verification against `pptx_exporter` synthetic payloads vs `solva_v2_sessions`).

## Honest follow-up list (DEV_PIPELINE.md §9 candidates)

Per the dispatch's report-only mandate on P1.2 + P1.4:

- **pip-audit follow-ups:** _none_. All 7 vulns are MITIGATED via the existing `IGNORED_VULNS` env tied to `backend/SECURITY_EXCEPTIONS.md`. Sunset conditions (listed in that file): when `emergentintegrations` upstream bumps `openai>=2.0`, re-evaluate the litellm CVE cluster. Not in P1 scope.
- **yarn audit follow-ups:** _none above threshold_. 16 Low + 24 Moderate findings remain in Dependabot's slow-burn channel per `dep-audit.yml` workflow comment at line 34. The pre-existing dependabot lane (`origin/dependabot/npm_and_yarn/frontend/*`) — 5 of which were just deleted during AUDIT_P0 history scrub — is the canonical pickup point for these. No new §9 row needed.
