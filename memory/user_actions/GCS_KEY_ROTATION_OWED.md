# GCS Key Rotation Owed

## Standing debt (2026-07-02)

**Two SA JSON keys are chat-exposed in this session's history:**
- `8b9c67705542eb0de08b70449723b79262c16d16` (original, from creds-stash side task)
- `518d39e162508fb2aaf4f1d6543ed8d7d59b8707` (rotation attempt that leaked in chat)

**Current live key** (per user rotation): whichever is at `/root/gcs-service-account.json` following their console rotation and (implicit) terminal swap. Determined by canary against that file.

**User disposition (verbatim)**: "Continue - no risk - skip step continue on the rest. use credentials"

**Standing rule invoked and overridden**: `CREDENTIALS_NEVER_IN_CHANNEL_RULE.md` (banked 2026-07-02). User has explicit authority to override on a per-event basis; the rule remains standing for future events. This override is FOR THIS INCIDENT ONLY, not a rescission of the rule.

**Rotation debt owed at next natural opportunity**: fresh key via terminal-only, delete BOTH `8b9c...` and `518d...` from GCP console, update `/root/gcs-service-account.json` via terminal swap. Suggested cadence: alongside JC-ADMIN-CRED-ROTATION-AND-ENV-VAR-REWIRE (the ~155-file admin@akki.ai rotation already sitting in this same queue).

**Do NOT auto-rotate**: rotation requires user's GCP console access. Debt visible here so it doesn't age silently.

---

## Current-key identification (populated by Phase 2 canary probe)

### 2026-07-02 canary attempt (Phase 2 · post user override "Continue - no risk")

- File at `/root/gcs-service-account.json` currently holds:
  - private_key_id prefix: `8b9c6770` (matches the ORIGINAL chat-exposed key `8b9c67705542eb0de08b70449723b79262c16d16` — i.e., the pre-rotation state)
  - client_email: `akki-executive-storage@digital-groove-495501-d3.iam.gserviceaccount.com`
- Canary result: **RED** · `upload_from_string failed: ('invalid_grant: Invalid JWT Signature.', {'error': 'invalid_grant', 'error_description': 'Invalid JWT Signature.'})`
- Diagnosis (per Phase 2 predicted failure mode): GCP-console-side rotation deleted the old key, so the JWT the file signs with is no longer trusted by GCP. The **terminal file swap did not land** — `/root/gcs-service-account.json` still contains the (now-dead) `8b9c...` key material. Fresh-key content is presumably held in the user's clipboard / a GCP-download / a local machine, but has not been written into the pod.

- Next action owed to user: complete the terminal swap of `/root/gcs-service-account.json` with fresh JSON (mode 600). No agent-side rotation possible without user's GCP console access.
