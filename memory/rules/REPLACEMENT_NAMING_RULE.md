# REPLACEMENT_NAMING_RULE (standing rule · banked 2026-07-02)

## Rule

> **When a specced verification step is replaced during execution, the report names it as a REPLACEMENT with the reason** — never as a profile footnote or silent substitution. Every future sprint memo where a specced step was replaced MUST include an explicit "Replacements" section citing the original spec + the replacement + the reason.

## Rationale

A silent substitution looks like the spec was followed; a named replacement makes the deviation legible. Legibility protects future readers (including humans reviewing the dispatch trail) from mistakenly assuming the spec was followed verbatim. This also creates an audit line that surfaces permission-scope drift, API-shape drift, and other environmental realities that would otherwise decay into folklore.

## Worked example (GCS stash side task · 2026-07-02)

- **Original spec:** "run this Python one-liner to `list_buckets` and print `buckets_in_project: [...]`".
- **Replacement:** per-bucket `list_blobs(target_name, max_results=1)` used instead.
- **Reason:** The scoped SA (`akki-executive-storage@digital-groove-495501-d3.iam.gserviceaccount.com`) has bucket-object-level permissions only. Project-level `storage.buckets.list` returns 403. `list_blobs` on a named bucket uses `storage.objects.list` which IS granted at bucket scope.
- **Impact:** The verification result is materially the same (bucket exists + SA can enumerate contents), but the impl uses a permission the SA actually holds. Documented in `/app/memory/user_actions/GCS_CREDS_STASHED.md` and cited on line 1 of the GCS build sprint memo.

## Scope

- **Applies to:** every sprint memo where a specced verification, endpoint, contract shape, or fixture step is replaced during implementation.
- **Format:** a "Replacements" section in the memo. One row per replacement: original spec + replacement + reason + evidence link.
- **Does NOT apply to:** additive extensions (new proving-slice rows added on top of specced ones), scope reductions explicitly authorized by the user, or refactors that don't change the specced verification's semantics.

## Cross-reference

- `/app/memory/DEV_PIPELINE.md` §9 — "Replacement-naming enforcement" checkable at any future review.
- `/app/memory/rules/TAB_HONESTY_RULE.md` — sibling standing rule (2026-07-02).
- First application: `/app/memory/sprints/JC_STORAGE_PIVOT_GCS_BUILD.md` cites the `list_buckets → list_blobs` replacement in its header.
