**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution cluster diagnosis · env_or_motor_loop_state)

# Pollution cluster — `env_or_motor_loop_state`

- **FTT IDs**: FTT-015, FTT-016, FTT-017, FTT-018
- **Polluted targets**: 2
  - `tests/test_phase_p3_2_cookie_hardening.py`
  - `tests/test_phase_p5_10_audit_panel_direct_linkage.py`

## Leaked state
Cookie-hardening + audit-panel tests depend on env values set by tests earlier in the suite (e.g. `SESSION_COOKIE_*`, `AKKI_AUDIT_LINK_*`). When the upstream test mutates these with `os.environ[...] = ...` (NOT via monkeypatch) and neglects to restore, the env persists into these tests. Conversely, when the upstream test DOES use monkeypatch but at module scope (rare), restoration happens too late.

## Isolation passes
- ✅ PASS in isolation — `tests/test_phase_p3_2_cookie_hardening.py`
  > 2 passed, 21 warnings in 4.63s

--STDERR--

## Static polluter candidate hits
| pattern | file | line | snippet |
|---|---|---:|---|
| `env_mutation_without_cleanup` | `backend/tests/deploy/test_compose_boot_smoke.py` | 179 | `os.environ["INTERNAL_TRANSPORT_SECRET"] = (` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_admin_email_provider_health.py` | 172 | `monkeypatch.setenv("SENDGRID_FROM_EMAIL", "noreply@example.com")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_admin_email_provider_health.py` | 173 | `monkeypatch.setenv("SENDGRID_INBOUND_DOMAIN", "inbound.example.com")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_admin_email_provider_health.py` | 174 | `monkeypatch.setenv("SENDGRID_INBOUND_AUTH_USERNAME", "sg-u")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_admin_email_provider_health.py` | 175 | `monkeypatch.setenv("SENDGRID_INBOUND_AUTH_PASSWORD", "sg-p")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_admin_email_provider_health.py` | 191 | `monkeypatch.setenv("SENDGRID_API_KEY", "SG.fake-key-for-warning-check")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_admin_email_provider_health.py` | 192 | `monkeypatch.setenv("SENDGRID_FROM_EMAIL", "noreply@example.com")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_admin_email_provider_health.py` | 193 | `monkeypatch.setenv("SENDGRID_INBOUND_DOMAIN", "inbound.example.com")` |
| `env_mutation_without_cleanup` | `backend/tests/test_chat_phase_b_p0_fix.py` | 37 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"  # hermetic — no live LLM` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_clamav_integration.py` | 157 | `monkeypatch.setenv("AKKI_ENV", "production")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_clamav_integration.py` | 158 | `monkeypatch.setenv("ALLOW_UNSAFE_UPLOADS", "true")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_clamav_integration.py` | 167 | `monkeypatch.setenv("AKKI_ENV", "development")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_clamav_integration.py` | 168 | `monkeypatch.setenv("ALLOW_UNSAFE_UPLOADS", "true")` |
| `env_mutation_without_cleanup` | `backend/tests/test_hardening_step3_demo_seed_boot.py` | 79 | `os.environ["DISABLE_DEMO_SEED"] = prior` |
| `env_mutation_without_cleanup` | `backend/tests/test_hardening_step3_demo_seed_boot.py` | 116 | `os.environ["DISABLE_DEMO_SEED"] = prior` |
| `env_mutation_without_cleanup` | `backend/tests/test_hardening_step3_demo_seed_boot.py` | 151 | `os.environ["DISABLE_DEMO_SEED"] = prior` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_hardening_step3_demo_seed_boot.py` | 188 | `monkeypatch.setenv("DISABLE_DEMO_SEED", "1")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_home_cleanup_phase_f6_debt.py` | 174 | `monkeypatch.setenv("SENDGRID_INBOUND_AUTH_USERNAME", "sg-user")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_home_cleanup_phase_f6_debt.py` | 175 | `monkeypatch.setenv("SENDGRID_INBOUND_AUTH_PASSWORD", "sg-pass-123")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_p0_c_oauth_session_ingestion.py` | 278 | `monkeypatch.setenv("COOKIE_SECURE", "0")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_p1_b_cohort_approval_email.py` | 121 | `monkeypatch.setenv("COHORT_EMAILS_ENABLED", "false")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_p1_b_cohort_approval_email.py` | 169 | `monkeypatch.setenv("COHORT_EMAILS_ENABLED", "true")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_p1_b_cohort_approval_email.py` | 221 | `monkeypatch.setenv("COHORT_EMAILS_ENABLED", "true")` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase4_2_http_transport_smoke.py` | 210 | `os.environ["BOUNDED_CONTEXT_TRANSPORT"] = "http"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase5_cron_split_smoke.py` | 102 | `os.environ["AKKI_PROCESS_NAME"] = orig` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_phase_a_chat_streaming_audit.py` | 92 | `monkeypatch.setenv("EMERGENT_LLM_KEY", "stub-key-for-tests")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_phase_b_chat_stream.py` | 85 | `monkeypatch.setenv("EMERGENT_LLM_KEY", "stub-key-for-tests")` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_b_p1_risks.py` | 37 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_c_chat_protective_layer.py` | 36 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_c_fix_bundle.py` | 81 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_d_fix_bundle.py` | 37 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_d_solva_pipeline.py` | 46 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_e_polish.py` | 39 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_f1_capability_gaps.py` | 54 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_f_engine_signals.py` | 43 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_phase_i4c_google_calendar.py` | 147 | `monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_ID", "test-client-id.apps.googleusercon` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_phase_i4c_google_calendar.py` | 148 | `monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_SECRET", "test-secret")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_phase_i4c_google_calendar.py` | 149 | `monkeypatch.setenv("GOOGLE_OAUTH_REDIRECT_URI", "https://test/api/oauth/google/` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_phase_i4c_google_calendar.py` | 166 | `monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_ID", "x")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_phase_i4c_google_calendar.py` | 167 | `monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_SECRET", "x")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_phase_i4c_google_calendar.py` | 168 | `monkeypatch.setenv("GOOGLE_OAUTH_REDIRECT_URI", "https://x/cb")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_phase_m2hold_cohort_hold.py` | 181 | `monkeypatch.setenv(` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_phase_m2hold_cohort_hold.py` | 184 | `monkeypatch.setenv("SENDGRID_API_KEY", "SG.fake-key")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_phase_m2hold_cohort_hold.py` | 185 | `monkeypatch.setenv("SENDGRID_FROM_EMAIL", "akki@syni.ai")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_phase_m2prep_notify_multirecipient.py` | 79 | `monkeypatch.setenv(` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_phase_m2prep_notify_multirecipient.py` | 82 | `monkeypatch.setenv("SENDGRID_API_KEY", "SG.fake-key-for-test")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_phase_m2prep_notify_multirecipient.py` | 83 | `monkeypatch.setenv("SENDGRID_FROM_EMAIL", "akki@syni.ai")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_phase_m2prep_notify_multirecipient.py` | 98 | `monkeypatch.setenv(` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_phase_m2prep_notify_multirecipient.py` | 101 | `monkeypatch.setenv("SENDGRID_API_KEY", "SG.fake-key-for-test")` |
| `monkeypatch_setenv_module_scope` | `backend/tests/test_phase_m2prep_notify_multirecipient.py` | 102 | `monkeypatch.setenv("SENDGRID_FROM_EMAIL", "akki@syni.ai")` |

_…and 59 more hits (truncated)._

## Dynamic confirmation
_(skipped — see slice header for the rationale.)_

## Recommended cleanup
Replace bare `os.environ[K] = v` mutations with `monkeypatch.setenv(K, v)` (fixture-scoped, auto-restored). Static guard via the polymorphic-response-ratchet pattern: AST-scan for `os.environ[` mutations in test code.
