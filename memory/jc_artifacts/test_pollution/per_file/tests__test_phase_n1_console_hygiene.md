**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_phase_n1_console_hygiene.py`

- **Bucket**: `PASS`
- **Duration**: 4.74 s
- **Return code**: 0

## STDOUT tail
```

tests/test_phase_n1_console_hygiene.py::test_n1_work_studio_page_size_literal_within_backend_cap
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_n1_console_hygiene.py::test_n1_work_studio_page_size_literal_within_backend_cap
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_n1_console_hygiene.py::test_n1_work_studio_page_size_literal_within_backend_cap
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_n1_console_hygiene.py::test_n1_work_studio_page_size_literal_within_backend_cap
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_n1_console_hygiene.py::test_n1_work_studio_page_size_literal_within_backend_cap
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
SKIPPED [1] tests/test_phase_n1_console_hygiene.py:77: Superseded by Phase Z-slice-2 (2026-05-27) — `union_of` fetch removed entirely; WorkStudio now hits the unified GET /api/contexts/{cid}/documents endpoint. See `test_phase_z_documents_journal.py::test_Z2_i_fetcher_hits_documents_endpoint_with_category` for the post-Z lock.
4 passed, 1 skipped, 21 warnings in 3.57s
```