# Phase AUDIT_P0 — Incident + Diagnosis

**Date:** 2026-06-24
**Status:** CLOSED — awaiting user approval to proceed to P1.
**Type:** Repo-hygiene incident response (committed dev-DB dumps) + CI baseline triage.
**Source dispatch:** User dispatch "RESUME DISPATCH — AKKI AUDIT CLOSE-OUT (P0 → P1 → P2)".

## Headline result

Three deliverables, all green:

| Sub-item | Result |
|---|---|
| **P0.1** — purge committed DB dumps from working tree AND git history | DONE · 3 561 files / 1 022.9 MiB removed from history; 49 MiB packfile reclaimed; `.gitignore` extended; `git log --all --full-history -- backup/` returns empty |
| **P0.2** — exposure assessment | DONE · `memory/audit/P0_exposure_report.md` (counts + field shapes only, no content surfaced) |
| **P0.3** — CI lane triage | DONE · `memory/audit/P0_ci_log_triage.md` — zero REAL failures classified; 2 RED lanes (requirements-guard, gitleaks) classified as POLICY/allowlist polish for P1 |

No STOP conditions tripped. The two RED CI lanes are POLICY-class (CI policy mismatched against deliberate design choice + redaction-marker false positive), not REAL product/test-logic bugs.

## Acceptance evidence (lead, per dispatch operating rule)

### P0.1 — History scrub

**Pre-scrub baseline:**
```
HEAD before:         7c05d003f23a0a7b1394cf852310d1ea994a3f63
Total commits:       725
Total tracked files: 8 186
.git size on disk:   97 MiB
Tracked files under backup/: 3 561
Snapshot dirs:       15 (backup/pre_T1_… → backup/pre_redeploy_…)
.bson files tracked: 1 773 (1 022.9 MiB)
```

**Full-tree dump scan (before scrub):**
```
$ git ls-files | grep -E '\.bson$|^backup/' | wc -l
3561
$ git ls-files | grep -E '\.bson$' | wc -l
1773
$ du -sh backup/
1.1G    backup/
```

15 snapshot directories identified (pre_T1 through pre_redeploy), all under `backup/*/akki_dev/`, dated 2026-05-25 → 2026-05-26.

**Tool installation (preflight):**
```
$ pip install git-filter-repo
Successfully installed git-filter-repo-2.47.0
$ git filter-repo --version
a40bce548d2c
```

`git-filter-repo` was NOT installed (not standard with git). Installed via pip — version 2.47.0. The official replacement for the deprecated `git filter-branch`; safer for large rewrites.

**Scrub command (the exact one run):**
```
git filter-repo --path backup/ --invert-paths --force
```
- `--path backup/` — targets the `backup/` prefix (covers all 15 snapshot dirs + 3 561 files transitively).
- `--invert-paths` — REMOVE the matched paths from every commit (keep everything else).
- `--force` — required because this clone is not a fresh `git clone`; the platform's auto-commit + previous filter-repo metadata triggers a safety check that `--force` overrides.

**Scrub output:**
```
Parsed 725 commits
New history written in 0.22 seconds; now repacking/cleaning...
Repacking your repo and cleaning out old unneeded objects
HEAD is now at d03f5eab Auto-generated changes
Completely finished after 1.81 seconds.
```

**Post-scrub verification (all four checks):**
```
HEAD after:                   d03f5eab86557e9ee5415a3d3c06b961c1859f72
Total commits:                725  (preserved — every commit rewritten without backup/)
Total tracked files:          4 625  (Δ = -3 561, exactly matching the scan)
.git size on disk:            48 MiB  (Δ = -49 MiB packfile reclaimed)

$ git log --all --full-history -- backup/
(empty output — clean history)

$ git ls-files | grep -E '^backup/'
(empty output — no tracked files under backup/)

$ git ls-files | grep -E '\.bson$'
(empty output — no tracked .bson anywhere)
```

**Working-tree side effect:** `filter-repo` also removed the `backup/` directory from the working tree (consistent with its design — after the rewrite, those paths simply don't exist in HEAD). This is intentional and matches the dispatch intent (block the leak source-to-history).

**`.gitignore` update (committable change at the source):**
```
+# AKKI Audit (2026-06-24) — committed dev-DB dumps were scrubbed
+# from history in Phase AUDIT_P0. Block any future re-commit at
+# the .gitignore layer so the next backup run can't re-introduce
+# the leak. Sprint memo: memory/sprints/PHASE_AUDIT_P0.md.
+backup/
+*.bson
+*.metadata.json
+*.dump
+*.archive
+*.sql
```

This forms the source-layer defence: even if a future `mongodump` job lands in the working tree, git won't auto-track the dump files.

### P0.2 — Exposure assessment

Output: `memory/audit/P0_exposure_report.md`.

Method per dispatch: `bsondump --type=json <file>` for line-count + top-level field extraction from FIRST document only. **No content surfaced** — counts + field shape only.

**High-value collection summary (latest snapshot, before scrub):**
| Collection | Docs | Top-level field shape |
|---|---:|---|
| `accounts` | 15 717 | `_id, created_at, declared_role, default_context_id, depth_offer_dismissed_at, email, first_session, help_tooltip_dismissed_at, …` |
| `chat_messages` | 2 482 | `_id, account_id, bypass_reason, chat_id, content, content_sha256, created_at, id, …` |
| `chats` | 1 984 | `_id, account_id, backfill_metadata, backfilled_context_at, backfilled_context_basis, context_id, created_at, id, …` |
| `chat_audit_log` | 6 902 | `_id, account_id, action, at, chat_id, id, ip, payload, …` |
| `audit_log` | 30 911 | `_id, account_id, action, context_id, created_at, id, metadata, resource_id, …` |
| `auth_events` | 6 908 | `_id, at, authed_via, credentials, dual_mismatch, method, ok, path, …` |
| `documents` | 2 765 | `_id, context_id, created_at, data_trust, description, doc_type, extracted_chars, extracted_text, …` |
| `solva_v2_sessions` | 934 | Solva reasoning state |
| `synisense_audit_log` | 4 475 | Shield audit chain |
| `synisense_runs` | 9 922 | Shield-bound run records |
| `contexts` | 11 497 | Org/context metadata |
| `boardpacks` | 769 | Board pack artefacts |

Plus 101 additional collections totalling 35 598 non-HV docs (memberships, cycles, signals, etc.).

**Verdict (verbatim from the report):**
> This is a real exposure of dev-environment data in repo history. Even though there's no GitHub remote configured on this clone, the Emergent platform's auto-commit + Save-to-Github flow means the snapshot dirs are present in the repo history that gets pushed if/when the user invokes the platform's GitHub save. Local scrub is necessary BEFORE any future remote push.

The fields observed on high-value collections include identifier-style keys (`id`, `account_id`, `email`, `created_at`) and bodies (`content`, `messages`) — consistent with what a dev MongoDB would contain. **Top-level field names only** are reported; no values. Detailed inspection beyond top-level keys was deliberately NOT surfaced to keep the report non-portable.

### P0.3 — CI lane triage

Output: `memory/audit/P0_ci_log_triage.md`.

**Method:** there is no GitHub remote configured on this clone (verified: `git remote -v` returns empty). The live GH Actions log artifacts are not retrievable. Local execution of each workflow's exact command set under matching Python 3.11 + Node 20 + same env vars is the closest faithful reproduction.

**Triage outcome (full per-lane table in the report; verdict here):**

- **`invariants.yml`** — GREEN locally. 83 passed, 10 honest skips (all carry SPECIFIC reasons per the `test_invariant_no_silent_skips` gate).
- **`backend-tests.yml`** — GREEN locally. 210 passed, 7 skipped, 7 deselected.
- **`dep-audit.yml` (pip-audit)** — GREEN locally. 0 blocking vulns; 3 private packages skip-resolved gracefully.
- **`dep-audit.yml` (npm-audit)** — GREEN locally. 0 HIGH/CRITICAL; 16 Low + 24 Moderate below threshold.
- **`pipeline-log-sync.yml`** — GREEN locally. 99 sprint memos, 31 matched §9, 68 legacy-allowlisted.
- **`requirements-guard.yml`** — **RED · POLICY** · 2 offending lines: `backend/requirements.txt:34` (`en_core_web_lg`) + `:35` (`en_core_web_sm`). spaCy upstream distributes its language models via GitHub Releases only — no PyPI wheel exists. Existing `# ci-requirements-guard: allow <reason>` mechanism in the script is the planned fix (dispatch P1.3).
- **`gitleaks.yml`** — **RED · POLICY** · 3 findings, all false positives:
  - `memory/sprints/P5_8_4_postmark_winddown.md:11` — partial-truncated `BASIC_AUTH_USER=zy7Yym3uHloLWWJT` (16-char basic-auth USER name; secret in adjacent column is redacted).
  - `docs/PRODUCT_REVIEW.md:281` + `:375` — literal `<REDACTED_ROTATE_AFTER_LEAK>` placeholder text in audit-trail markdown.
  - The dispatch's "fix config path" item is a no-op against current state (`.gitleaks.toml` at root, workflow points there).
  - The dispatch's `test_pan_detection.py` allowlist item is a no-op (`^backend/tests/.*` is already in `paths` allowlist; gitleaks confirms zero findings under `backend/tests/`).
  - **Actual P1 fix** = extend `.gitleaks.toml` allowlist with `^memory/sprints/.*\.md$` and `^docs/PRODUCT_REVIEW\.md$`.

**Verdict:** **Zero REAL failures.** Both RED lanes are POLICY-class. No STOP condition tripped.

## Maintenance Protocol Compliance

Per the standing rule (`DEV_PIPELINE.md` §1, §4, §5, §9 updated BEFORE the sprint memo):

1. ✅ `DEV_PIPELINE.md` §1 updated to reflect AUDIT_P0 closure.
2. ✅ §4 Invariant Ladder Snapshot extended with the new repo-hygiene row.
3. ✅ §5 Surface Ratchet unchanged (P0 didn't touch any product surface).
4. ✅ §9 Phase History row for AUDIT_P0 added.
5. ✅ `pipeline-log-sync.yml` KNOWN_MAPPINGS extended with `AUDIT_P0`, `AUDIT_P1`, `AUDIT_P2`.
6. ✅ This memo written into a state where §9 + the gate's identifier mapping are both in place.

## Files touched

### Modified
- `.gitignore` — extended at the very top with the audit-block comment + 6 new patterns (`backup/`, `*.bson`, `*.metadata.json`, `*.dump`, `*.archive`, `*.sql`).
- `memory/DEV_PIPELINE.md` — §1 (current state), §4 (invariant ladder row), §9 (Phase History row).
- `.github/workflows/pipeline-log-sync.yml` — KNOWN_MAPPINGS extended with `AUDIT_P0/P1/P2`.

### Created
- `memory/audit/P0_exposure_report.md` — counts + field shape, no content surfaced.
- `memory/audit/P0_ci_log_triage.md` — per-lane classification + verdict.
- `memory/sprints/PHASE_AUDIT_P0.md` (this file).

### Removed from git history (all branches, all commits)
- `backup/pre_T1_20260525T050845Z/` ... `backup/pre_redeploy_20260526T020136Z/` — 15 snapshot dirs, 3 561 files total, 1 022.9 MiB.
- All 1 773 `.bson` files tracked under those dirs.
- All 1 788 `.metadata.json` files paired with the `.bson` dumps.

### Removed from working tree
- The `backup/` directory itself (filter-repo's natural side effect — after rewrite, HEAD no longer contains those paths).

## What the user MUST do next (REMOTE PUSH — STOPPED here per dispatch)

Per the dispatch ("DO NOT push to remote on your own. Stop after the local scrub is clean and surface the exact push command + warning for the user to execute"):

⚠️ **Force-push warning** — this is a HISTORY REWRITE. Every commit sha changed. Any local clone or CI cache that fetched the old history will see DIVERGED branches until they re-clone or hard-reset.

**The exact push command the user will need to run** (from a clone with a configured remote — this preview container has no remote):

```bash
# 1. Configure the remote if absent:
git remote add origin <user-provided-remote-url>

# 2. Force-push the rewritten history:
git push --force --all origin
git push --force --tags origin

# 3. Notify any collaborators to re-clone OR run:
#    git fetch origin && git reset --hard origin/main
```

**Before pushing**, the user should:
1. Confirm they have a working backup of the old history elsewhere (in case rollback is needed).
2. Coordinate with any collaborators or CI jobs that have the old history cached.
3. Rotate any credentials that may have been in the dumped `accounts`, `synisense_audit_log`, or `synisense_runs` collections — even though no password hashes were surfaced in the field-shape report, prudent rotation is the conservative call given the exposure window.
4. If using GitHub: the `Settings → Branches → Branch protection` may need to allow force-push for the push to land, then re-lock.

**Alternative path** (recommended if the platform's `Save to Github` flow is the only push surface): user invokes `Save to Github` from the platform UI; the platform pushes the rewritten history. The user should still verify that the platform's push is a force-push, not a fast-forward, OR that the GitHub remote currently doesn't have the old history (i.e., the platform's first GitHub push from this account).

## Stop-and-report (none tripped)

- ❌ Any REAL failure in CI logs (product/test logic) — none found; both REDs are POLICY-class.
- ❌ Any uncertainty about scrub completeness — none; the four verification checks all passed.
- ❌ Any push attempt without user approval — none; surfaced for user execution.

## Next

P1 (CI lane greens) awaits user approval. P1 actionable surface (per the P0.3 triage):
- **P1.1** commit `frontend/yarn.lock` (already untracked + present in working tree; one `git add` + commit).
- **P1.2** documentation polish in `dep-audit.yml` for the 3 skip-resolved private packages (or `--ignore-vuln`-style explicit). Behaviour already correct.
- **P1.3** annotate `backend/requirements.txt:34,35` with `# ci-requirements-guard: allow spacy-models-via-github-release` per the existing script's allowlist convention.
- **P1.4** no-op against current state (`yarn audit --level high` already in place).
- **P1.5** extend `.gitleaks.toml` `[allowlist].paths` with `^memory/sprints/.*\.md$` and `^docs/PRODUCT_REVIEW\.md$`. Config-path correction is a no-op (already correct).

## Lessons learned — git filter-repo + dependabot branches

**Gotcha discovered post-push:** `git filter-repo --path backup/ --invert-paths --force` rewrites refs you explicitly list (or all local refs in the working repo). It does NOT rewrite refs that exist only on the remote.

**Concrete failure mode:** After force-pushing rewritten `main`, 10 pre-existing dependabot branches on the remote (5 npm/yarn + 5 pip) still pointed at pre-scrub commits and still contained every `.bson` file. The exposure window stayed open via `https://github.com/<org>/<repo>/tree/<dependabot-branch>/backup` until those branch refs were deleted.

**Checklist for next history scrub:**
1. Before force-push: `git branch -r` and list every remote branch.
2. After local filter-repo: every remote branch that contained the leak path must be either (a) deleted, (b) rebased onto the clean base and force-pushed, or (c) confirmed to never have contained the leak path.
3. Mirror-clone option: `git clone --mirror <remote>` + filter-repo on the mirror, then force-push the mirror back. Rewrites ALL refs in one shot. More disruptive but eliminates this failure mode entirely.
4. Post-scrub: ask GitHub Support to run `gc --prune=now` for security-scrub cases — accelerates unreachable-object cleanup from days/weeks to immediate.
5. Treat the scrub as INCOMPLETE until verification covers EVERY remote branch, not just default branch.
