# Credentials Never In Channel

**Rule**: Credentials (private keys, service-account JSON, DB connection strings, API tokens, passwords) move through mounts and file swaps — never conversation.

**Enforcement path**:
- Rotation flows: user places new credential via VS Code terminal swap into the mounted path (e.g., `/root/gcs-service-account.json`), never via chat paste.
- Agent-to-orchestrator: agents reference credentials by file path + expected env var name, never by value.
- Orchestrator-to-user: guides + step-by-step, never a request to paste a credential inline.

**Provenance (2026-07-02)**: Third credential incident in this session — (i) admin@akki.ai plaintext leaked via smoke-test message → deferred rotation queued; (ii) GCS SA JSON paste in creds-stash side task → rotation gate raised; (iii) Stage 1 close gate re-surfaced rotation, and orchestrator's option (a) "paste it here" re-reproduced the same exposure vector. Banked as permanent standing rule so it stops being re-decided per event.

**Applies to**: every future credential handoff without exception.
