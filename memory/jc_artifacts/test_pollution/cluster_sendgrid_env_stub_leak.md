**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (cross-test pollution cluster diagnosis · sendgrid_env_stub_leak)

# Pollution cluster — `sendgrid_env_stub_leak`

- **FTT IDs**: FTT-019, FTT-020, FTT-021, FTT-022
- **Polluted targets**: 1
  - `tests/test_phase_p5_7_5_bounce_webhook.py`

## Leaked state
Bounce-webhook tests expect `SENDGRID_INBOUND_PARSE_SECRET` and friends to be present + match the canonical fixture. Upstream tests set/unset `SENDGRID_*` env vars for their own scenarios without restoration. Conftest's `COHORT_NOTIFY_DISABLED=true` short-circuit also affects what env shape the bounce path expects.

## Isolation passes
- ✅ PASS in isolation — `tests/test_phase_p5_7_5_bounce_webhook.py`
  > 5 passed, 21 warnings in 4.27s

--STDERR--

## Static polluter candidate hits
| pattern | file | line | snippet |
|---|---|---:|---|
| `env_mutation_without_cleanup` | `backend/tests/deploy/test_compose_boot_smoke.py` | 179 | `os.environ["INTERNAL_TRANSPORT_SECRET"] = (` |
| `env_mutation_without_cleanup` | `backend/tests/test_chat_phase_b_p0_fix.py` | 37 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"  # hermetic — no live LLM` |
| `env_mutation_without_cleanup` | `backend/tests/test_hardening_step3_demo_seed_boot.py` | 79 | `os.environ["DISABLE_DEMO_SEED"] = prior` |
| `env_mutation_without_cleanup` | `backend/tests/test_hardening_step3_demo_seed_boot.py` | 116 | `os.environ["DISABLE_DEMO_SEED"] = prior` |
| `env_mutation_without_cleanup` | `backend/tests/test_hardening_step3_demo_seed_boot.py` | 151 | `os.environ["DISABLE_DEMO_SEED"] = prior` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase4_2_http_transport_smoke.py` | 210 | `os.environ["BOUNDED_CONTEXT_TRANSPORT"] = "http"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase5_cron_split_smoke.py` | 102 | `os.environ["AKKI_PROCESS_NAME"] = orig` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_b_p1_risks.py` | 37 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_c_chat_protective_layer.py` | 36 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_c_fix_bundle.py` | 81 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_d_fix_bundle.py` | 37 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_d_solva_pipeline.py` | 46 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_e_polish.py` | 39 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_f1_capability_gaps.py` | 54 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_f_engine_signals.py` | 43 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_p3_1_csrf.py` | 63 | `os.environ["CSRF_TEST_BYPASS_HEADER"] = "0"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_p3_1_csrf.py` | 68 | `os.environ["CSRF_TEST_BYPASS_HEADER"] = old` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_p3_1_csrf.py` | 96 | `os.environ["CSRF_TEST_BYPASS_HEADER"] = "0"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_p3_1_csrf.py` | 101 | `os.environ["CSRF_TEST_BYPASS_HEADER"] = old` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_p3_1_csrf.py` | 128 | `os.environ["CSRF_TEST_BYPASS_HEADER"] = "0"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_p3_1_csrf.py` | 133 | `os.environ["CSRF_TEST_BYPASS_HEADER"] = old` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_p5_8_inbox_migration.py` | 95 | `os.environ["INBOUND_PROVIDER"] = "postmark"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_p5_8_inbox_migration.py` | 112 | `os.environ["INBOUND_PROVIDER"] = "sendgrid"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_zz2_x.py` | 139 | `os.environ["AKKI_CHAT_FIXTURES_ENABLED"] = "1"` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_zz2_x.py` | 168 | `os.environ["AKKI_CHAT_FIXTURES_ENABLED"] = saved_env` |
| `env_mutation_without_cleanup` | `backend/tests/test_phase_zz2_x.py` | 176 | `os.environ["AKKI_CHAT_FIXTURES_ENABLED"] = "1"` |
| `env_mutation_without_cleanup` | `backend/tests/test_qa_chunk_10.py` | 37 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_qa_chunk_11.py` | 36 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_qa_chunk_12.py` | 39 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_qa_chunk_13.py` | 151 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_qa_chunk_14.py` | 48 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_qa_chunk_15.py` | 61 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_qa_chunk_16.py` | 49 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_qa_chunk_18.py` | 197 | `os.environ["SYNISENSE_LLM_MODE"] = ""` |
| `env_mutation_without_cleanup` | `backend/tests/test_qa_chunk_18.py` | 219 | `os.environ["SYNISENSE_LLM_MODE"] = saved_mode` |
| `env_mutation_without_cleanup` | `backend/tests/test_qa_chunk_18.py` | 244 | `os.environ["SYNISENSE_LLM_MODE"] = ""` |
| `env_mutation_without_cleanup` | `backend/tests/test_qa_chunk_18.py` | 261 | `os.environ["SYNISENSE_LLM_MODE"] = saved_mode` |
| `env_mutation_without_cleanup` | `backend/tests/test_qa_chunk_18_5.py` | 54 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_qa_chunk_18_5.py` | 76 | `os.environ["SYNISENSE_LLM_MODE"] = saved` |
| `env_mutation_without_cleanup` | `backend/tests/test_qa_chunk_7.py` | 46 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_qa_chunk_8.py` | 47 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_qa_chunk_9.py` | 40 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_qa_chunk_9_5.py` | 42 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_synisense_e2e.py` | 47 | `os.environ["SYNISENSE_LLM_MODE"] = "mock"` |
| `env_mutation_without_cleanup` | `backend/tests/test_synisense_encryption.py` | 34 | `os.environ[k] = v` |
| `env_mutation_without_cleanup` | `backend/tests/test_synisense_encryption.py` | 44 | `os.environ["SYNISENSE_MASTER_KEY"] = _fresh_hex()` |
| `env_mutation_without_cleanup` | `backend/tests/test_synisense_encryption.py` | 56 | `os.environ["SYNISENSE_MASTER_KEY"] = k_v1` |
| `env_mutation_without_cleanup` | `backend/tests/test_synisense_encryption.py` | 64 | `os.environ["SYNISENSE_MASTER_KEY_V2"] = _fresh_hex()` |
| `env_mutation_without_cleanup` | `backend/tests/test_synisense_encryption.py` | 73 | `os.environ["SYNISENSE_MASTER_KEY"] = _fresh_hex()` |
| `env_mutation_without_cleanup` | `backend/tests/test_synisense_encryption.py` | 86 | `os.environ["AKKI_ENV"] = "production"` |

_…and 2 more hits (truncated)._

## Dynamic confirmation
_(skipped — see slice header for the rationale.)_

## Recommended cleanup
Same cleanup discipline as cluster 6 (monkeypatch.setenv + static guard). Additionally: bounce-webhook tests should pin all their required env vars at fixture scope, not rely on conftest defaults.
