**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_render_determinism.py`

- **Bucket**: `PASS`
- **Duration**: 5.65 s
- **Return code**: 0

## STDOUT tail
```
tests/test_render_determinism.py::test_deck_pptx_deterministic
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_render_determinism.py::test_deck_pptx_deterministic
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_render_determinism.py::test_deck_pptx_deterministic
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_render_determinism.py::test_deck_pptx_deterministic
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_render_determinism.py::test_deck_pptx_deterministic
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
SKIPPED [1] tests/test_render_determinism.py:99: Patch 19 — fixture pollution under full-suite. Passes in isolation. Companion to test_report_docx_deterministic above.
SKIPPED [1] tests/test_render_determinism.py:118: Patch 19 — passes in isolation but fails under full-suite due to fixture/render order pollution. Needs per-test fixture isolation.
4 passed, 2 skipped, 21 warnings in 4.34s
```