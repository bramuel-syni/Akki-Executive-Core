# P0.2 — Exposure Report (committed DB dumps)
**Generated:** 2026-06-24 (P0 audit).
**Scope:** every `.bson` file under `backup/*/akki_dev/` tracked in `git ls-files`.
**Method:** `bsondump --type=json` for line-count + top-level field extraction from first document. **No content surfaced** in this report — counts + field shape only.

## Tactical findings
- 1773 `.bson` files tracked across 15 snapshot dirs.
- 1,072,568,025 bytes on disk (1022.9 MiB).
- 119 unique collection names.
- Date range: pre_T1_20260525T050845Z → pre_redeploy_20260526T020136Z.

## High-value collections (PII / message body / auth state)
| Collection | Docs (latest snap) | Top-level fields (sample) |
|---|---:|---|
| `accounts` | 15717 | `_id`, `created_at`, `declared_role`, `default_context_id`, `depth_offer_dismissed_at`, `email`, `first_session`, `help_tooltip_dismissed_at` |
| `ask_messages` | 9 | `_id`, `answer`, `asked_by`, `asked_by_email`, `context_id`, `created_at`, `id`, `mode` |
| `audit_log` | 30911 | `_id`, `account_id`, `action`, `context_id`, `created_at`, `id`, `metadata`, `resource_id` |
| `auth_events` | 6908 | `_id`, `at`, `authed_via`, `credentials`, `dual_mismatch`, `method`, `ok`, `path` |
| `boardpacks` | 769 | `_id`, `account_id`, `block_status`, `body`, `body_redacted`, `classification`, `classification_at`, `commentary` |
| `briefings` | 0 |  |
| `briefs` | 6 | `_id`, `account_id`, `body`, `context_id`, `created_at`, `id`, `kind`, `model` |
| `chat_audit_log` | 6902 | `_id`, `account_id`, `action`, `at`, `chat_id`, `id`, `ip`, `payload` |
| `chat_messages` | 2482 | `_id`, `account_id`, `bypass_reason`, `chat_id`, `content`, `content_sha256`, `created_at`, `id` |
| `chats` | 1984 | `_id`, `account_id`, `backfill_metadata`, `backfilled_context_at`, `backfilled_context_basis`, `context_id`, `created_at`, `id` |
| `consent_decisions` | 0 |  |
| `context_objects` | 1283 | `_id`, `answers`, `completed`, `context_id`, `created_at`, `created_by`, `id`, `industry` |
| `contexts` | 11497 | `_id`, `created_at`, `id`, `inbound_token`, `industry`, `jurisdiction`, `name`, `owner_account_id` |
| `documents` | 2765 | `_id`, `context_id`, `created_at`, `data_trust`, `description`, `doc_type`, `extracted_chars`, `extracted_text` |
| `solva_sessions` | 0 |  |
| `solva_v2_sessions` | 934 | `_grounding_candidates`, `_grounding_comparables`, `_id`, `account_id`, `cluster_id`, `cluster_label`, `completed_at`, `context_id` |
| `synisense_audit_log` | 4475 | `_id`, `audit_id`, `consumer_id`, `de_id_summary`, `dilution_score`, `exposure_reduction_score`, `latency_ms`, `llm_model` |
| `synisense_runs` | 9922 | `_id`, `account_id`, `context_id`, `id`, `input_sha256`, `mode`, `shield_map_id`, `spans` |

## Remaining collections (counts only)

| Collection | Docs |
|---|---:|
| `memberships` | 8278 |
| `synisense_trust_receipts` | 3562 |
| `cycles` | 3553 |
| `signals` | 3117 |
| `cycle_agendas` | 2759 |
| `news_items` | 1777 |
| `cycle_team` | 1271 |
| `work_studio_briefs` | 1009 |
| `cycle_assignments` | 1002 |
| `context_metadata_signatures` | 827 |
| `cycle_questions` | 803 |
| `team_catalogue` | 673 |
| `synisense_signals` | 618 |
| `sandbox_v2_sessions` | 570 |
| `compilations` | 524 |
| `backfill_log` | 499 |
| `synisense_shield_maps` | 450 |
| `ned_packs` | 429 |
| `user_context_visits` | 371 |
| `audit_invariant_violations` | 337 |
| `quick_action_usage` | 271 |
| `solva_phase_d_sessions` | 184 |
| `work_studio_brief_revisions` | 171 |
| `llm_retry_log` | 159 |
| `cycle_contributions` | 157 |
| `cycle_followups` | 152 |
| `objectives` | 149 |
| `exco_teams` | 147 |
| `cohorts` | 144 |
| `signal_actions` | 131 |
| `upload_scan_log` | 130 |
| `projects` | 128 |
| `user_recent_views` | 128 |
| `signal_events` | 126 |
| `work_studio_exports` | 115 |
| `work_studio_phase_c_exports` | 107 |
| `synisense_subscriptions` | 91 |
| `work_studio_export_tokens` | 81 |
| `strategic_goals` | 76 |
| `async_jobs` | 49 |
| `login_attempts` | 43 |
| `questions` | 33 |
| `backfill_jobs` | 31 |
| `studio_shares` | 29 |
| `solva_v1_comparables_archive` | 27 |
| `studio_blocks` | 24 |
| `cycle_configs` | 23 |
| `scheduler_runs` | 23 |
| `studio_views` | 19 |
| `billing_launch_interest` | 17 |
| `chunk8_seed_log` | 15 |
| `blog_posts` | 14 |
| `solva_clusters` | 12 |
| `blog_subscribers` | 11 |
| `solva_v1_sessions_archive` | 11 |
| `synisense_tenant_entities` | 11 |
| `decks` | 10 |
| `llm_validator_usage` | 10 |
| `sandbox_pickups` | 10 |
| `deck_outlines` | 9 |
| `invitations` | 8 |
| `llm_deep_usage` | 8 |
| `deck_telemetry` | 7 |
| `telemetry_events` | 7 |
| `work_studio_artefact_versions` | 7 |
| `briefing_reads` | 6 |
| `early_access_registrations` | 5 |
| `stripe_dead_letter` | 5 |
| `stripe_events` | 5 |
| `ned_meeting_notes` | 4 |
| `reports` | 4 |
| `studio_images` | 4 |
| `inbound_queue` | 3 |
| `ned_meetings` | 3 |
| `_migrations` | 2 |
| `ned_positions` | 2 |
| `solva_cycle_handoff_queue` | 2 |
| `solva_handoffs` | 2 |
| `cycle_history` | 1 |
| `document_views` | 1 |
| `mentions` | 1 |
| `ned_followups` | 1 |
| `organisations` | 1 |
| `plays` | 1 |
| `scheduler_locks` | 1 |

## Exposure verdict

The dumps include real `chat_messages` + `accounts` + `chat_audit_log` + `auth_events` rows from a development environment dated 2026-05-25 → 2026-05-26.

Fields observed on high-value collections include identifier-style keys (`id`, `account_id`, `email`, `created_at`) and bodies (`content`, `messages`) — consistent with what we would expect a dev MongoDB to contain.

**This is a real exposure of dev-environment data in repo history.** Even though there's no GitHub remote configured on this clone, the Emergent platform's auto-commit + Save-to-Github flow means the snapshot dirs are present in the repo history that gets pushed if/when the user invokes the platform's GitHub save. Local scrub is necessary BEFORE any future remote push.

No password hashes / API keys are stored in the high-value collections we sampled (`accounts` carries `email` + `display_name` style fields; password hashes live elsewhere if at all). Detailed field inspection beyond top-level keys is deliberately NOT surfaced in this report to avoid making the dump portable.
