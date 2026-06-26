**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_home_cleanup_phase_e3_scope_compliance.py`

- **Bucket**: `PASS`
- **Duration**: 11.84 s
- **Return code**: 0

## STDOUT tail
```
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_home_cleanup_phase_e3_scope_compliance.py::test_scope_prompted_edit_endpoint_wired_through_shield
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_home_cleanup_phase_e3_scope_compliance.py::test_scope_prompted_edit_endpoint_wired_through_shield
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_home_cleanup_phase_e3_scope_compliance.py::test_scope_prompted_edit_endpoint_wired_through_shield
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_home_cleanup_phase_e3_scope_compliance.py::test_scope_prompted_edit_endpoint_wired_through_shield
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

tests/test_home_cleanup_phase_e3_scope_compliance.py::test_scope_pdf_watermark_actually_embedded_in_bytes
tests/test_home_cleanup_phase_e3_scope_compliance.py::test_scope_download_draft_includes_watermarked_pdf
  /root/.venv/lib/python3.11/site-packages/pypdf/_page.py:1197: DeprecationWarning: Calling `PageObject.replace_contents()` for pages not assigned to a writer is deprecated and will be removed in pypdf 7.0.0. Attach the page to the writer first or use `PdfWriter(clone_from=...)` directly. The existing approach has proved being unreliable.
    self.replace_contents(ContentStream(new_content_array, self.pdf))

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
15 passed, 23 warnings in 10.14s
```