**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_synisense_integration.py`

- **Bucket**: `PASS`
- **Duration**: 18.2 s
- **Return code**: 0

## STDOUT tail
```
    @app.on_event("startup")

tests/test_synisense_integration.py::test_contract_shape
  /app/backend/akki_app.py:318: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_synisense_integration.py::test_contract_shape
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_synisense_integration.py::test_contract_shape
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

tests/test_synisense_integration.py::test_contract_shape
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

tests/test_synisense_integration.py::test_contract_shape
tests/test_synisense_integration.py::test_spans_non_overlapping_sorted
tests/test_synisense_integration.py::test_replacement_tokens_unique_per_match
tests/test_synisense_integration.py::test_stats_populated
tests/test_synisense_integration.py::test_perf_buffer_populated
  /root/.venv/lib/python3.11/site-packages/pydantic/main.py:464: UserWarning: Pydantic serializer warnings:
    PydanticSerializationUnexpectedValue(Expected 10 fields but got 7: Expected `Message` - serialized value may not be as expected [field_name='message', input_value=Message(content='```json\... 'thinking_blocks': []}), input_type=Message])
    PydanticSerializationUnexpectedValue(Expected `StreamingChoices` - serialized value may not be as expected [field_name='choices', input_value=Choices(finish_reason='st...ider_specific_fields={}), input_type=Choices])
    return self.__pydantic_serializer__.to_python(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
8 passed, 26 warnings in 16.67s
```