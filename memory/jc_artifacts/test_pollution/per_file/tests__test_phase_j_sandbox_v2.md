**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` (per-file subprocess capture · cluster diagnosis)

# Per-file capture · `tests/test_phase_j_sandbox_v2.py`

- **Bucket**: `PASS`
- **Duration**: 34.08 s
- **Return code**: 0

## STDOUT tail
```
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

tests/test_phase_j_sandbox_v2.py::test_solva_v2_accepts_sandbox_flag
tests/test_phase_j_sandbox_v2.py::test_create_session_bearer_works_against_solva_v2
  /root/.venv/lib/python3.11/site-packages/pydantic/main.py:464: UserWarning: Pydantic serializer warnings:
    PydanticSerializationUnexpectedValue(Expected 10 fields but got 7: Expected `Message` - serialized value may not be as expected [field_name='message', input_value=Message(content='```json\... 'thinking_blocks': []}), input_type=Message])
    PydanticSerializationUnexpectedValue(Expected `StreamingChoices` - serialized value may not be as expected [field_name='choices', input_value=Choices(finish_reason='st...ider_specific_fields={}), input_type=Choices])
    return self.__pydantic_serializer__.to_python(

tests/test_phase_j_sandbox_v2.py::test_solva_v2_accepts_sandbox_flag
  /root/.venv/lib/python3.11/site-packages/pydantic/main.py:464: UserWarning: Pydantic serializer warnings:
    PydanticSerializationUnexpectedValue(Expected 10 fields but got 5: Expected `Message` - serialized value may not be as expected [field_name='message', input_value=Message(content="You've g...ields={'refusal': None}), input_type=Message])
    PydanticSerializationUnexpectedValue(Expected `StreamingChoices` - serialized value may not be as expected [field_name='choices', input_value=Choices(finish_reason='st...ider_specific_fields={}), input_type=Choices])
    return self.__pydantic_serializer__.to_python(

tests/test_phase_j_sandbox_v2.py::test_create_session_bearer_works_against_solva_v2
  /root/.venv/lib/python3.11/site-packages/pydantic/main.py:464: UserWarning: Pydantic serializer warnings:
    PydanticSerializationUnexpectedValue(Expected 10 fields but got 5: Expected `Message` - serialized value may not be as expected [field_name='message', input_value=Message(content="You've n...ields={'refusal': None}), input_type=Message])
    PydanticSerializationUnexpectedValue(Expected `StreamingChoices` - serialized value may not be as expected [field_name='choices', input_value=Choices(finish_reason='st...ider_specific_fields={}), input_type=Choices])
    return self.__pydantic_serializer__.to_python(

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
29 passed, 25 warnings in 32.10s
```