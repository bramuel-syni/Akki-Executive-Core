Canonical rationale: gitleaks Path A allowlist extension + 3-step canary proof. User dispatch 2026-07-08 · `JC-GITLEAKS-PATH-A-ALLOWLIST-AND-CANARY` (option b · pinned+SHA-verified install · exactly 5 path-anchored entries · zero wildcards · 3-step canary in exact order · lane closes ONLY on all-three-green).

# JC-GITLEAKS-PATH-A-ALLOWLIST-AND-CANARY · HARD-STOPPED

**Status:** 🔴 **HARD-STOPPED · NOT-SHIPPED · surface-blocker surfaced**  
**Priority:** P1  
**PRE_ARC_HEAD:** `1fe2493b` (§9 row 🟡 IN-FLIGHT flip, pre-code-touch, pre-install)

---

## Received-scope amendment(s) echo (4 items)

- (C-1) Pinned + SHA-verified install from official GitHub releases to `/usr/local/bin/`; no `curl | bash`.
- (C-2) Exactly 5 path-anchored regex entries; zero wildcards; one cause comment per entry.
- (C-3) 3-step canary in exact order: baseline exit 0 → canary hit non-zero → cleanup exit 0.
- (C-4) Lane closes ONLY on all-three-green.

---

## STEP 1 · Install log (PASS)

**Pinned version chosen:** `v8.18.4` (well-known stable v8.x line release from mid-2024; latest tag lookup via `api.github.com` returned 403 due to unauthenticated rate-limit — chose known-stable pinned version rather than attempting authenticated call which would require credentials).

**Pod architecture:** `aarch64` (verified via `uname -m`) → target binary: `linux_arm64`.

**Download URL:** `https://github.com/gitleaks/gitleaks/releases/download/v8.18.4/gitleaks_8.18.4_linux_arm64.tar.gz` (via `wget`, not `curl | bash`).

**Checksums URL:** `https://github.com/gitleaks/gitleaks/releases/download/v8.18.4/gitleaks_8.18.4_checksums.txt` (downloaded separately).

**SHA-256 verification:**
```
computed = bf5f7f466ebfade1296c8bd32cf7d3f592c2aa78836aa9980ffbe2cadca7a861
expected = bf5f7f466ebfade1296c8bd32cf7d3f592c2aa78836aa9980ffbe2cadca7a861
            (grep 'linux_arm64' /tmp/gitleaks_checksums.txt)
MATCH ✅
```

**Install:** `tar -xzf gitleaks_8.18.4_linux_arm64.tar.gz && install -m 0755 gitleaks /usr/local/bin/gitleaks`.

**Verify:** `/usr/local/bin/gitleaks version` → `8.18.4` ✅.

---

## STEP 2 · Config edit (PASS · applied exactly as specified)

`/app/.gitleaks.toml` extended with **EXACTLY 5 path-anchored regex entries** under `[allowlist]` → `paths = [...]`. Zero wildcards. One cause comment above each. No other change to the file.

```toml
  # placeholder tokens <pass>, <PROD_ATLAS_URI> in production env runbook
  '''^docs/RUNBOOKS/PRODUCTION_ENV\.md$''',
  # deployment doc placeholder tokens
  '''^docs/DEPLOYMENT\.md$''',
  # product spec placeholder tokens
  '''^docs/PRODUCT_SPEC\.md$''',
  # SG.fake-key-for-warning-check fixture used by provider health test
  '''^backend/tests/test_admin_email_provider_health\.py$''',
  # Azure engineer request notes containing documented placeholder secrets
  '''^memory/user_actions/AZURE_ENGINEER_REQUEST.*\.md$''',
```

---

## STEP 3 · 3-step canary proof · HARD-STOPPED AT STEP (a)

### Step (a) · Baseline scan (of committed git history — what CI runs by default)

```
$ gitleaks detect --config .gitleaks.toml --no-banner --report-format json --report-path /tmp/gitleaks_git_only.json
scan completed in 10.6s
911 commits scanned.
leaks found: 6
exit code = 1  (baseline is NOT clean)
```

**Result: FAIL — baseline exit code is 1, not 0.**

### Step (a) findings enumerated (6 leaks in committed git history)

| # | RuleID | File | Line | Secret prefix (first 12 chars) |
|---|---|---|---|---|
| 1 | `generic-api-key` | `memory/evidence/2026_07_02/bundle_v0_5_owner_digest/HALTED.md` | 13 | `SG.keVt_ghmS...` |
| 2 | `generic-api-key` | `memory/jc_artifacts/JC-TM-compile-session-pre-commit.json` | 27 | `P3KcTZacUmSO...` |
| 3 | `generic-api-key` | `memory/jc_artifacts/JC-TM-compile-session-pre-commit.json` | 44 | `bQxMrZnFgxz0...` |
| 4 | `generic-api-key` | `memory/jc_artifacts/JC-WS-A-BoardPack-detail-view-state.json` | 48 | `cd5ef68f5389...` |
| 5 | `generic-api-key` | `memory/jc_artifacts/JC-WS-A-BoardPack-detail-view-state.json` | 139 | `cd5ef68f5389...` |
| 6 | `generic-api-key` | `memory/jc_artifacts/JC-WS-A-BoardPack-detail-view-state.json` | 240 | `44136fa355b3...` |

### Additional forensic — working-tree scan (`--no-git`) finds 19 leaks including untracked files

Working-tree-only findings (in addition to the 6 above; **these are NOT in committed git history**):
- `backend/.env` (8 hits · **untracked · not in `git ls-files`** — `.gitignore` line 169 has `!backend/.env` negation but the file is not tracked; these are pod-local env values)
- `.secrets/B3_standby_keys.md` (2 hits · `.gitignore` line 20 excludes `/.secrets/`)
- `backend/.pytest_cache/v/cache/nodeids` (4 hits · pytest cache, gitignored)

These working-tree-only findings do NOT affect the CI git-history scan; they are documented here for completeness.

---

## STEP 4 · The mismatch surface — user direction required

**The 5 entries specified by the dispatch do NOT target any of the 6 files that are actually producing hits in the CI-mode scan.**

| Dispatch-targeted file | Hits in working-tree scan | Hits in git-history scan |
|---|---|---|
| `docs/RUNBOOKS/PRODUCTION_ENV.md` | **0** | 0 |
| `docs/DEPLOYMENT.md` | **0** | 0 |
| `docs/PRODUCT_SPEC.md` | **0** | 0 |
| `backend/tests/test_admin_email_provider_health.py` | **0** (already covered by pre-existing `^backend/tests/.*` entry) | 0 |
| `memory/user_actions/AZURE_ENGINEER_REQUEST*.md` | **0** | 0 |

**Meanwhile the 6 real hits are in files NOT in the dispatch's 5-entry list:**
- `memory/evidence/2026_07_02/bundle_v0_5_owner_digest/HALTED.md` (1)
- `memory/jc_artifacts/JC-TM-compile-session-pre-commit.json` (2)
- `memory/jc_artifacts/JC-WS-A-BoardPack-detail-view-state.json` (3)

**Additionally observed:** finding #1 (`SG.keVt_ghmS...` in `memory/evidence/.../HALTED.md`) has the **same first-12-char prefix** as the `SG.keVt_ghmSKaBRR7K9KSVtw.pDPW...` value present in `backend/.env` (untracked). This may indicate a **real SendGrid token committed to a memory/evidence file** — if so, it is a rotate-and-stash matter (Path B), not a config-fix matter (Path A). **This is not for the agent to unilaterally decide** — surfacing to user.

---

## STEP 5 · Actions NOT taken (per HARD-STOP-DO-NOT-IMPROVISE protocol)

- **Did NOT add 3 entries to cover the actual 6 hits** — the dispatch explicitly said "EXACTLY these 5 path-anchored regex entries" and "Zero wildcards" and I cannot add or modify entries beyond the specification.
- **Did NOT execute steps (b) or (c) of the canary** — the dispatch requires baseline exit 0 as prerequisite for step (b); without a clean baseline, step (b)'s "canary caught while everything else clean" semantics is ill-defined.
- **Did NOT proceed to `SHIPPED-UNPUSHED` claim** — the dispatch says "lane closes ONLY when green AND the canary proves a real leak is still detected". Baseline non-zero → lane NOT green → SHIPPED claim invalid.
- **Did NOT rotate the possibly-committed SendGrid token** — credential rotation requires user disposition; agent does not act on credentials unilaterally.

---

## STEP 6 · Actions taken (recorded)

- ✅ Downloaded pinned `gitleaks v8.18.4 linux_arm64` tarball; SHA-256 verified against release checksums file; MATCHED.
- ✅ Installed to `/usr/local/bin/gitleaks`; `gitleaks version` → `8.18.4`.
- ✅ Added the 5 specified path-anchored regex entries to `/app/.gitleaks.toml` under `[allowlist] → paths = [...]` (zero wildcards, one cause comment per entry, no other file changes).
- ✅ Ran baseline scan (step a); surface baseline-non-zero condition with objective evidence.
- ✅ Ran working-tree scan for completeness; enumerated all 19 findings by file/rule/line/secret-prefix.
- ✅ Confirmed 5-entry allowlist targets have 0 hits in either scan mode (the config edit is a no-op against current state).
- ✅ Composed this hard-stop memo + proving slice + banking to `/app/memory/audit/gitleaks_path_a_canary_2026_07_08.md`.

---

## STEP 7 · User direction requested (choose one)

- **(A) Bank the 5 entries as-instructed even though they're no-op** and I add the 3 additional entries needed to cover the actual 6 hits (2 files: `memory/jc_artifacts/JC-*.json` + `memory/evidence/.../HALTED.md`); after which baseline goes to 0 and I resume steps (b) + (c). **Note:** dispatch says "Zero wildcards" — I can encode these as specific path anchors (e.g. `^memory/jc_artifacts/JC-.*\.json$` + `^memory/evidence/2026_07_02/bundle_v0_5_owner_digest/HALTED\.md$`).
- **(B) Do NOT allowlist the `HALTED.md` SendGrid token — rotate it instead.** The token appears real (same 12-char prefix as the `backend/.env` untracked value). If it is a live SendGrid key committed to memory/evidence, that is a rotate-and-stash matter. User dispatches a separate rotation arc; this arc remains hard-stopped.
- **(C) Roll back the 5-entry edit as no-op** and hard-stop the arc entirely; user re-scopes the dispatch with the correct 3-entry list (memory/jc_artifacts/... + memory/evidence/...HALTED.md) and re-fires.
- **(D) Something else** — user directs.

---

## STEP 8 · Push status

**PUSH STATUS: NOT-SHIPPED** — the dispatch mandates "lane closes ONLY when green AND the canary proves a real leak is still detected"; baseline is not green; therefore this arc is NOT SHIPPED, is NOT closing, and does NOT flip §9 🟢. `/app/.gitleaks.toml` edit remains committed as-is (contains the user-specified 5 entries) pending user direction; if user chooses option (C), the edit will be reverted.

**Commits made in this arc:**
- `1fe2493b` (§9 🟡 IN-FLIGHT · pre-code-touch)
- Pending: `.gitleaks.toml` edit + this memo + slice commit (to be committed together immediately below)

**Content marker (interim):** `gitleaks-path-a-hard-stopped-baseline-non-zero-mismatch-with-5-entry-spec`
