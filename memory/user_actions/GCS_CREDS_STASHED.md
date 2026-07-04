# GCS Credentials Stashed · 2026-07-02

- File: /root/gcs-service-account.json (mode 600, root-owned) — verified `-rw------- 1 root root 2410 Jul 4 15:13`
- Project ID: digital-groove-495501-d3
- Service account: akki-executive-storage@digital-groove-495501-d3.iam.gserviceaccount.com
- Bucket (verified via list_blobs at bucket-scope): **akki-executive-uploads-analyze** ✅ exists + SA has object-level access
- Gitignore: updated (`/root/gcs-service-account.json` + `*service-account*.json` + `gcs-*.json` patterns added to /app/.gitignore)
- Env vars: appended to /app/backend/.env (3 keys: `GOOGLE_APPLICATION_CREDENTIALS` + `GCP_PROJECT_ID` + `GCS_BUCKET_NAME`)
- Auth probe: **PASS (partial)** — SA authenticates successfully; `storage.buckets.list` and `storage.buckets.get` are DENIED at project scope but `storage.objects.list` on the target bucket IS GRANTED (this is the permission the app actually needs for upload/download flows)
- SA permission profile: bucket-object-level scoped (not project-wide). Consistent with least-privilege principle for a storage-only SA.
- Storage build dispatch: **QUEUED** · fires post-A7-SHIPPED on user direction (chain closed 2026-07-02; storage build is a separate dispatch)
- Backend restart: NOT PERFORMED (per user directive — env vars pick up on next natural restart)
- Rotation reminder: pasted key ID `8b9c67705542eb...` is compromised (chat history). **Rotate at end of storage build** — generate fresh key in GCP console, delete this one, update `/root/gcs-service-account.json`, verify probe still GREEN.

## Probe output (verbatim)

```
buckets_in_project: <403 · storage.buckets.list denied>
target_bucket_exists: <403 via buckets.get; but confirmed via list_blobs>
bucket-list-blobs-OK: akki-executive-uploads-analyze (first-page-size=0)
bucket-list-blobs-DENIED: akki-executive-uploads · NotFound · http=404
bucket-list-blobs-DENIED: akki-executive-storage · NotFound · http=404
bucket-list-blobs-DENIED: akki_executive_uploads_analyze · NotFound · http=404
```

## Notes for storage build dispatch

- SA has `storage.objects.list` on target bucket → likely also has `storage.objects.get` and `storage.objects.create` (typical bundled grant). Storage build proving slice should test upload + download + list against the bucket to confirm exact permission set.
- SA lacks `storage.buckets.list` and `storage.buckets.get` at project level — the storage-build implementation MUST NOT rely on `client.list_buckets()` or `client.get_bucket(name)` for pre-flight checks. Use direct `client.bucket(name)` (does NOT call GCS API) + `list_blobs(max_results=1)` for connectivity verification.
- Empty bucket at time of stash (first-page-size=0) — expected for fresh provisioning.
