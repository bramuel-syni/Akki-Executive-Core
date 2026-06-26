**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_phase_z2_batch3.py`

- **Bucket**: `PASS`
- **Duration**: 8.52 s
- **Return code**: 0

## STDOUT tail
```
          
    @app.on_event("startup")

tests/test_phase_z2_batch3.py::test_z2_5_trash_icon_only_for_uploaded_rows
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_z2_batch3.py::test_z2_5_trash_icon_only_for_uploaded_rows
tests/test_phase_z2_batch3.py::test_z2_5_backend_delete_upload_then_listing_skips_archived
tests/test_phase_z2_batch3.py::test_z2_5_backend_rejects_akki_generated_with_403
tests/test_phase_z2_batch3.py::test_z2_5_backend_404_for_missing_doc
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_z2_batch3.py::test_z2_5_trash_icon_only_for_uploaded_rows
tests/test_phase_z2_batch3.py::test_z2_5_backend_delete_upload_then_listing_skips_archived
tests/test_phase_z2_batch3.py::test_z2_5_backend_rejects_akki_generated_with_403
tests/test_phase_z2_batch3.py::test_z2_5_backend_404_for_missing_doc
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_z2_batch3.py::test_z2_5_trash_icon_only_for_uploaded_rows
tests/test_phase_z2_batch3.py::test_z2_5_backend_delete_upload_then_listing_skips_archived
tests/test_phase_z2_batch3.py::test_z2_5_backend_rejects_akki_generated_with_403
tests/test_phase_z2_batch3.py::test_z2_5_backend_404_for_missing_doc
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
13 passed, 39 warnings in 7.07s
```