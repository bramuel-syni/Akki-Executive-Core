**Canonical Spec**: `/app/memory/audit/PHASE_5_6_1_CSRF_RIG_AUDIT.md` (structural enforcement: tests that assert nothing hide gaps)

# Thin-assertion baseline scan · 20260626T174822Z

- **Files walked**: 434
- **Findings (raw)**: 9
- **Findings (allowlisted via `@pytest.mark.acceptable_thin_assertion` + `# reason:` comment)**: 0
- **Findings (ACTIVE — must close or allowlist)**: **9**
- **Halt threshold (>10 → HALT)**: ✅ OK

## Pattern catalog

| ID | Pattern | Reason it's thin |
|---|---|---|
| T1 | `try: pass` (no assertion inside the try body) | Test runs zero substantive assertions — the `try` swallows nothing meaningful. |
| T2 | body == `pass` (with optional docstring) | No statements executed under test. |
| T3 | `assert <constant>` (e.g. `assert True`) | Constant assertion exercises nothing. |
| T4 | body contains only `pytest.skip(...)` | Marker the test should be deleted or rewritten, not green-by-default. |
| T5 | docstring-only body | Specification without verification. |

## Active findings
| # | Pattern | File | Line | Function | Evidence |
|---:|---|---|---:|---|---|
| 1 | `T2` | `backend/tests/test_iter12_shares_home.py` | 190 | `test_comment_on_share_via_comments_router` | `body == pass` |
| 2 | `T3` | `backend/tests/test_j2_stage_3.py` | 438 | `test_no_guardrail_files_modified_in_j2` | `assert True` |
| 3 | `T3` | `backend/tests/test_j3_stage_4_5_frontend.py` | 210 | `test_j3_f6_retired_at_j4_ship` | `assert True` |
| 4 | `T3` | `backend/tests/test_j3_stage_4_5_frontend.py` | 231 | `test_j3_f8_no_guardrail_files_modified` | `assert True` |
| 5 | `T4` | `backend/tests/test_patch_21_news.py` | 141 | `test_news_endpoint_requires_auth` | `only pytest.skip(...)` |
| 6 | `T4` | `backend/tests/test_patch_23_upload_p0.py` | 61 | `test_upload_endpoint_rejects_without_auth_header` | `only pytest.skip(...)` |
| 7 | `T4` | `backend/tests/test_patch_25_news_geo.py` | 206 | `test_profile_country_get_patch_round_trip` | `only pytest.skip(...)` |
| 8 | `T2` | `backend/tests/test_track_b_phase1_signin_begin.py` | 200 | `test_fig20_unauth_root_lands_on_signin` | `body == pass` |
| 9 | `T2` | `backend/tests/test_track_b_phase1_signin_begin.py` | 211 | `test_fig22_post_redirect_no_error_state` | `body == pass` |
