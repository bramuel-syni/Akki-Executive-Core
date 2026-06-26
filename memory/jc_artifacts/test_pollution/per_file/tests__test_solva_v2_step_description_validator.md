**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_solva_v2_step_description_validator.py`

- **Bucket**: `PASS`
- **Duration**: 4.95 s
- **Return code**: 0

## STDOUT tail
```
          
    return self.router.on_event(event_type)  # ty: ignore[deprecated]

tests/test_solva_v2_step_description_validator.py::test_observational_descriptions_pass[Layer 1 Surface \u2014 extracting 4 candidate framings]
  /app/backend/solva_app.py:108: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_solva_v2_step_description_validator.py::test_observational_descriptions_pass[Layer 1 Surface \u2014 extracting 4 candidate framings]
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_solva_v2_step_description_validator.py::test_observational_descriptions_pass[Layer 1 Surface \u2014 extracting 4 candidate framings]
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_solva_v2_step_description_validator.py::test_observational_descriptions_pass[Layer 1 Surface \u2014 extracting 4 candidate framings]
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_solva_v2_step_description_validator.py::test_observational_descriptions_pass[Layer 1 Surface \u2014 extracting 4 candidate framings]
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
27 passed, 21 warnings in 3.69s
```