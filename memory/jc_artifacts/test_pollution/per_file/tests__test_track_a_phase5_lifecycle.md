**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_track_a_phase5_lifecycle.py`

- **Bucket**: `PASS`
- **Duration**: 58.0 s
- **Return code**: 0

## STDOUT tail
```
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

server.py:362
  /app/backend/server.py:362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

server.py:1303
  /app/backend/server.py:1303: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("startup")

server.py:1362
  /app/backend/server.py:1362: DeprecationWarning: 
          on_event is deprecated, use lifespan event handlers instead.
  
          Read more about it in the
          [FastAPI docs for Lifespan Events](https://fastapi.tiangolo.com/advanced/events/).
          
    @app.on_event("shutdown")

tests/test_track_a_phase5_lifecycle.py::test_phase5_schema_additive_fields_persist
  /root/.venv/lib/python3.11/site-packages/pydantic/main.py:464: UserWarning: Pydantic serializer warnings:
    PydanticSerializationUnexpectedValue(Expected 10 fields but got 5: Expected `Message` - serialized value may not be as expected [field_name='message', input_value=Message(content='# Reason...ields={'refusal': None}), input_type=Message])
    PydanticSerializationUnexpectedValue(Expected `StreamingChoices` - serialized value may not be as expected [field_name='choices', input_value=Choices(finish_reason='st...ider_specific_fields={}), input_type=Choices])
    return self.__pydantic_serializer__.to_python(

tests/test_track_a_phase5_lifecycle.py::test_phase5_schema_additive_fields_persist
  /root/.venv/lib/python3.11/site-packages/pydantic/main.py:464: UserWarning: Pydantic serializer warnings:
    PydanticSerializationUnexpectedValue(Expected 10 fields but got 5: Expected `Message` - serialized value may not be as expected [field_name='message', input_value=Message(content='```json\...ields={'refusal': None}), input_type=Message])
    PydanticSerializationUnexpectedValue(Expected `StreamingChoices` - serialized value may not be as expected [field_name='choices', input_value=Choices(finish_reason='st...ider_specific_fields={}), input_type=Choices])
    return self.__pydantic_serializer__.to_python(

tests/test_track_a_phase5_lifecycle.py::test_phase5_schema_additive_fields_persist
  /app/backend/services/work_studio_export.py:315: FutureWarning: Truth-testing of elements was a source of confusion and will always return True in future versions. Use specific 'len(elem)' or 'elem is not None' test instead.
    rFonts = rPr.find(qn("w:rFonts")) or OxmlElement("w:rFonts")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
14 passed, 1 deselected, 24 warnings in 56.14s
```