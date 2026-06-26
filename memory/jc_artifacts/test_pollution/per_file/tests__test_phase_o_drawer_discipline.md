**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_phase_o_drawer_discipline.py`

- **Bucket**: `PASS`
- **Duration**: 4.89 s
- **Return code**: 0

## STDOUT tail
```

tests/test_phase_o_drawer_discipline.py::test_o_compliant_surfaces_use_doc_id_url_contract
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_o_drawer_discipline.py::test_o_compliant_surfaces_use_doc_id_url_contract
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_o_drawer_discipline.py::test_o_compliant_surfaces_use_doc_id_url_contract
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_o_drawer_discipline.py::test_o_compliant_surfaces_use_doc_id_url_contract
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_phase_o_drawer_discipline.py::test_o_compliant_surfaces_use_doc_id_url_contract
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ============================
SKIPPED [1] tests/test_phase_o_drawer_discipline.py:109: Superseded by Phase Z-slice-2 (2026-05-27) — DocumentCardsSection REMOVED from WorkStudio.jsx (unified documents listing subsumes its role). The canonical-URL contract is preserved by DocumentRow's onOpen handler — see `test_phase_z_documents_journal.py::test_Z2_o_row_click_other_categories_open_via_doc_id`.
5 passed, 1 skipped, 21 warnings in 3.69s
```