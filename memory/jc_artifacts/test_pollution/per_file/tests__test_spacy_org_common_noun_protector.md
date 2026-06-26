**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_spacy_org_common_noun_protector.py`

- **Bucket**: `PASS`
- **Duration**: 6.16 s
- **Return code**: 0

## STDOUT tail
```
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_spacy_org_common_noun_protector.py::test_malaria_disease_name_not_redacted_as_org
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_spacy_org_common_noun_protector.py::test_malaria_disease_name_not_redacted_as_org
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_spacy_org_common_noun_protector.py::test_malaria_disease_name_not_redacted_as_org
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_spacy_org_common_noun_protector.py::test_malaria_disease_name_not_redacted_as_org
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

tests/test_spacy_org_common_noun_protector.py::test_org_protector_terms_constant_exported
  tests/test_spacy_org_common_noun_protector.py:75: PytestWarning: The test <Function test_org_protector_terms_constant_exported> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_org_protector_terms_constant_exported():

tests/test_spacy_org_common_noun_protector.py::test_org_protector_terms_does_not_overreach
  tests/test_spacy_org_common_noun_protector.py:84: PytestWarning: The test <Function test_org_protector_terms_does_not_overreach> is marked with '@pytest.mark.asyncio' but it is not an async function. Please remove the asyncio mark. If the test is not marked explicitly, check for global marks applied via 'pytestmark'.
    def test_org_protector_terms_does_not_overreach():

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
5 passed, 23 warnings in 4.36s
```