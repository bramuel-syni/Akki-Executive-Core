# TRUTH-IN-CAPABILITY RULE

**Canonical citation**: user amendment 2026-07-02 during `JC-STORAGE-PIVOT-GCS-BUILD` Stage 1 dispatch (in-flight amendment) + banked as standing rule.

**Rule** (one line):

> Do NOT claim a ceiling capability (e.g. "supports 500 MB uploads") until the **exact format the user actually uploads** ingests end-to-end at that ceiling. Transport landing in storage ≠ ingest capability. Report exactly what was proven, exactly what wasn't.

## Rationale

Two kinds of proof commonly get conflated when we ship a storage pivot:

1. **Transport proof** — bytes land in the target store at the target size. Round-trip integrity (SHA match, size match, exists() true). Says nothing about downstream use.
2. **Ingest proof** — the product code path (parse_workbook, extract text, retrieval, render, chart, etc.) accepts the file **at that same size** and returns a usable artefact **without exceeding pod / process resources or timing out**.

Claiming (1) implies (2) is dishonest — it papers over per-format peak-RAM cliffs, xml-attack costs, streaming assumptions, and worst-case time complexity, all of which vary sharply by format.

## Worked example (this dispatch)

- **Stage 1 (this dispatch)** proves TRANSPORT at 500 MB via GCS resumable upload session — bytes land in the bucket at exactly 500 MB, SHA verified, `bucket.blob(name).exists() == True`. ✅ **PROVEN**.
- **Stage 1 DOES NOT prove xlsx ingest at 500 MB.** The Path A acceptance uses a ~17-20 MB valid xlsx that Analyze successfully ingests and opens an artefact for; that proves ingest **at that size**, not at 500 MB. ✅ **PROVEN AT ~17 MB · NOT PROVEN AT 500 MB**.
- **Ingest capability per format at 500 MB is Stage 2 territory** — profile peak-RAM per format (CSV, xlsx, pdf, etc.), report PROVEN / AT RISK / BLOCKED per format, present costed options if BLOCKED (pod bump, convert-on-ingest, per-format cap).

Reporting for this dispatch says: **"Transport proven at 500 MB via resumable session. xlsx ingest proven at ~17 MB. xlsx ingest at 500 MB is NOT proven and is Stage 2 scope."** Anything terser than that is a violation.

## Application checklist

Before writing "supports X" in any sprint memo / CHANGELOG / dashboard row / user message:

1. Did the proving slice ingest a file **of that format** **at that size** **through the product code path** (not a synthetic bypass)?
2. Did the artefact / result / rendered output land successfully (not just "200 OK on the upload")?
3. Did the pod stay within memory / CPU / wall-clock budget?

If any answer is "no" or "didn't measure", the claim is TRANSPORT-only or SIZE-only — label it that way explicitly. Never round up.

## Cross-references

- `sprints/JC_STORAGE_PIVOT_GCS_BUILD.md` (this rule born mid-dispatch)
- `sprints/JC_STORAGE_STAGE_2_INGEST_PROFILING.md` (queued follow-up; per-format ingest profile at 500 MB)
- `rules/REPLACEMENT_NAMING_RULE.md` (companion standing rule — same discipline family: don't silently substitute proof geometry)
