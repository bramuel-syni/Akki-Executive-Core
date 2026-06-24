# P0.3 — CI Job Log Triage

**Generated:** 2026-06-24 (P0 audit close-out).
**Method:** ran each workflow's exact command set locally in the container. There is no GitHub remote configured on this clone, so live GH Actions log artifacts are not retrievable — local execution under the same env vars + Python 3.11 + Node 20 is the closest faithful reproduction.
**Classification grid:**
- **GREEN** — the lane passes locally end-to-end.
- **REAL** — failure is a product/test-logic bug; needs code change.
- **POLICY** — failure is a CI-policy mismatch against a deliberate design choice; needs allowlist/config update, not product code change.
- **ENV** — failure is toolchain/network/missing-dep; needs infra fix.

## Triage table

| Workflow | Step | Local exit | Classification | Evidence + next-action |
|---|---|---:|---|---|
| `invariants.yml` | `pytest tests/invariants/ -q --no-header -ra` | 0 (GREEN) | — | 83 passed, 10 honest skips (3 HUMAN_REQUIRED LLM transients + 7 deliberate-violation smoke sentinels). All skips carry SPECIFIC reasons per the `test_invariant_no_silent_skips` gate. |
| `backend-tests.yml` | targeted-green scope, `-m "not integration and not deploy_smoke"` | 0 (GREEN) | — | 210 passed, 7 skipped, 7 deselected. Same skip-reason discipline as above. |
| `dep-audit.yml` / `pip-audit` | `pip-audit -r backend/requirements.txt --format json` + Python triage block | 0 (GREEN) | — | 0 blocking vulns after the existing IGNORED_VULNS list (7 litellm CVEs). 3 packages skip-resolved gracefully (`en-core-web-lg`, `en-core-web-sm`, `emergentintegrations` — all private/local, not on PyPI). The workflow comment at lines 26-31 already documents this design choice. **P1 hygiene polish:** annotate the 3 skip lines in the workflow comment so reviewers don't re-discover them. |
| `dep-audit.yml` / `npm-audit` | `yarn audit --groups dependencies --level high` | 0 (GREEN) | — | 0 HIGH/CRITICAL vulns; 16 Low + 24 Moderate (below threshold). Matches the dispatch P1.4 acceptance ("high/critical only") — already in place. |
| `pipeline-log-sync.yml` | Python rendering of sprints/ ↔ §9 | 0 (GREEN) | — | 99 sprint memos, 31 matched §9, 68 legacy-allowlisted, zero unparseable. |
| `requirements-guard.yml` | `scripts/check_requirements_urls.py --root .` | 1 (RED) | POLICY | 2 offending lines — `backend/requirements.txt:34` (`en_core_web_lg @ https://github.com/.../*.whl`) and `:35` (`en_core_web_sm @ ...`). spaCy upstream distributes its language models via GitHub Releases only — there is no PyPI wheel for these. Per dispatch P1.3, **annotate** both lines with `# ci-requirements-guard: allow <reason>`. Self-test (`test_requirements_guard.py`) passes 8/1S, so the guard infra is healthy; the policy mismatch is in `requirements.txt` content. |
| `gitleaks.yml` | `gitleaks detect --no-banner --config .gitleaks.toml` | 1 (RED) | POLICY | 3 findings, ALL false positives: <br>• `memory/sprints/P5_8_4_postmark_winddown.md:11` — partial-truncated `BASIC_AUTH_USER=zy7Yym3uHloLWWJT` (16-char user identifier, NOT a secret — it's the basic-auth user *name*; the secret is the password in the next column, redacted). <br>• `docs/PRODUCT_REVIEW.md:281` — literal `<REDACTED_ROTATE_AFTER_LEAK>` placeholder text (i.e., gitleaks regex matched the redaction marker, not a real secret). <br>• `docs/PRODUCT_REVIEW.md:375` — same literal placeholder. <br>**Config-path correctness:** `.gitleaks.toml` exists at repo root and the workflow points to `.gitleaks.toml` — config path already correct. The dispatch P1.5's call to "correct config path" is a no-op against current state. <br>**`test_pan_detection.py` reference:** the dispatch mentions allowlisting `tests/.../test_pan_detection.py` fixtures, but the current `.gitleaks.toml` already has `^backend/tests/.*` in `paths` (line 27), and gitleaks confirmed no findings under `backend/tests/`. So this is also a no-op against current state. <br>**Actual P1 fix:** extend the `.gitleaks.toml` allowlist to cover `^memory/sprints/.*\.md$` and `^docs/PRODUCT_REVIEW\.md$` for redacted/placeholder content in audit-trail markdown. |
| `backend-tests.yml` (full tree, NOT the targeted-green slice) | — | — | DEFERRED | Phase 5.5.2 candidate C `broader-suite drift triage` — sized at ~7 unrelated test files with drift across earlier sprints. Out of P0/P1 audit scope; queued behind P2. |
| `codemod-drift.yml` | (not executed in this triage) | — | — | Mirrors a passing local codemod check; not flagged in the dispatch. |
| `deploy.yml`, `lighthouse.yml`, `marketing-assets-guard.yml`, `render-smoke.yml`, `voice-lint.yml` | (not executed) | — | — | Out of audit scope. |

## Verdict

**Zero REAL (product/test-logic) failures.** The two RED lanes (`requirements-guard`, `gitleaks`) are both POLICY-class — neither flags a product bug, neither indicates a leaked secret in current code. Both have one-line allowlist fixes mapped to dispatch items P1.3 (requirements-guard spaCy allow) and P1.5 (gitleaks allowlist extension).

Per the dispatch's STOP rule ("If any REAL failure exists, STOP P0 here and surface before proceeding to P1") — no REAL failure exists, so P0 proceeds to .gitignore + history scrub + sprint memo, then on user approval, P1 begins.

## Notes for the user

1. The dispatch's gitleaks "fix the config path" item is a no-op on current state — config is already at `.gitleaks.toml` at the repo root and the workflow already points there. The actual P1 fix is the allowlist extension above.
2. The dispatch's `tests/.../test_pan_detection.py` allowlist item is also a no-op — `^backend/tests/.*` is already in `paths` allowlist; gitleaks confirms zero findings under `backend/tests/`.
3. The pip-audit `emergentintegrations` exclusion item is functionally already in effect (pip-audit gracefully skip-resolves it because it isn't on PyPI). The P1 polish is documentation/comment, not a behaviour change.
4. The npm-audit "high/critical only" item is already in place (`yarn audit --level high`); P1.4 is a no-op against current state.

So the actionable surface for P1 is narrower than the dispatch implies: **P1.1 (commit yarn.lock), P1.3 (annotate spaCy lines), P1.5 (extend gitleaks allowlist)**. P1.2 and P1.4 are documentation/no-op confirmations.
