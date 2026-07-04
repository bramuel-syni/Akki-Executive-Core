# Amendment Echo Rule

**Rule**: Every amendment to an in-flight dispatch is echoed back in the NEXT board state as "received-scope" BEFORE build begins. A dispatch build cannot start on amended scope until the receiving agent has explicitly enumerated the amendment contents in a board state or memo header.

**Purpose**: Compaction silently drops amendments. Only echo-back reconciliation catches drops in hours, not post-ship.

**Enforcement**:
- Receiving agent opens the next board state with a "Received-scope amendment(s):" line listing every amendment ID + one-line summary.
- If build begins without the echo, orchestrator flags as procedural violation and re-issues.

**Provenance (2026-07-02)**: `JC-STORAGE-PIVOT-GCS-BUILD` shipped 12/12 GREEN but silently dropped the "CEILING LOCKED · STORAGE_MAX_UPLOAD_MB=500 · resumable · Stage 2 stub" amendment. Only the truth-in-capability reconciliation at close caught the gap. Banked to prevent recurrence.

**Applies to**: every future dispatch amendment without exception.
