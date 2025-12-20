# Review Model Command

Review a Pydantic model for Pydantic 2.0+ best practices, comparing against its SDK service class and OpenAPI schema.

## Arguments

- `$1` - Model file path (e.g., `scm/models/deployment/bgp_routing.py`)
- `$2` - Service class file path (e.g., `scm/config/deployment/bgp_routing.py`)
- `$3` - OpenAPI schema file path (e.g., `openapi-specs/deployment-services_new.yaml`)
- `$4` - Schema name in OpenAPI spec (e.g., `bgp-routing`) - optional, will be inferred from model path if not provided

## Workflow

Execute these phases in order. Use TodoWrite to track progress through each phase.

### Phase 1: Gather Context

#### Step 1.1 - Read the model file ($1)
Read the entire model file and identify:
- All Enum classes
- Base models
- Request models (CreateModel, UpdateModel)
- Response models
- Field definitions (types, defaults, descriptions)
- Validators (@field_validator)
- Serializers (@field_serializer)
- Model config (ConfigDict settings)

#### Step 1.2 - Read the SDK service class ($2)
Read the service class file and identify:
- ENDPOINT constant
- CRUD methods available (get, list, create, update, delete)
- How models are instantiated from input data
- How payloads are serialized for API requests
- How responses are parsed into models
- Any special handling (validation, conversion, error handling)

#### Step 1.3 - Read and parse the OpenAPI schema ($3)
Read the OpenAPI schema file and find the schema definition for the resource.
If $4 is provided, search for that schema name. Otherwise, infer from the model file name.

Identify from the OpenAPI schema:
- **Required fields**: Check for `required` array in schema definition
- **Optional fields**: Fields not in `required` array
- **Available endpoints**: Which HTTP methods exist (GET/POST/PUT/DELETE)
- **Singleton resource**: If only GET/PUT exist (no POST), it's a singleton
- **Field constraints**: enums, patterns, minLength, maxLength, minimum, maximum
- **Nested schemas**: Any $ref references to other schemas

#### Step 1.4 - Read related test files
Find and read:
- Model tests: `tests/scm/models/<category>/test_<model_name>_models.py`
- Service tests: `tests/scm/config/<category>/test_<model_name>.py`
- Test factories: `tests/factories/<category>/<model_name>.py`

### Phase 2: Analyze Against Best Practices

Apply this checklist to the model file:

| Check | Requirement | How to Verify |
|-------|-------------|---------------|
| `extra="forbid"` | All models must have `model_config = ConfigDict(extra="forbid")` | Search for ConfigDict in each model class |
| ConfigDict usage | Use `model_config = ConfigDict(...)` NOT `class Config:` | No `class Config:` should exist |
| Field optionality | Must match OpenAPI spec required/optional | Compare field definitions to OpenAPI `required` array |
| Default values | ResponseModel fields should have sensible defaults | Lists default to `[]`, bools to `False`, etc. |
| Validator patterns | Use `@field_validator("field", mode="before")` or `mode="after"` | Check all validators use correct Pydantic 2.0+ syntax |
| No cls.__name__ checks | Never branch validator logic based on class name | Search for `cls.__name__` or `self.__class__.__name__` |
| Serializer usage | Use `@field_serializer` for custom JSON output | Check serializers use Pydantic 2.0+ syntax |
| Model dump | Use `model_dump(exclude_unset=True)` for partial updates | Check service class update() method |
| Singleton handling | No CreateModel if API only has GET/PUT | If singleton, CreateModel should be alias for UpdateModel |
| Backwards compatibility | Keep old class names as aliases if renaming | Use `OldName = NewName` pattern |

### Phase 3: Document Findings

Create a structured report of issues found:

```
## Issues Found

### Critical (Must Fix)
- [ ] Issue description with file:line reference

### Recommended (Should Fix)
- [ ] Issue description with file:line reference

### Optional (Nice to Have)
- [ ] Issue description with file:line reference
```

Present findings to user and ask for confirmation before proceeding.

### Phase 4: Implement Changes

After user approval, implement fixes in this order:

#### 4.1 - Update model file
- Add/fix ConfigDict with `extra="forbid"`
- Fix field optionality to match OpenAPI
- Fix validators to use Pydantic 2.0+ patterns
- Remove any `cls.__name__` anti-patterns
- Add proper serializers
- Create backwards-compatible aliases if needed

#### 4.2 - Update service class
- For singletons: simplify create() to delegate to update()
- Ensure proper model_dump() usage with exclude_unset/exclude_none
- Handle edge cases in response parsing
- Fix any enum serialization

#### 4.3 - Update test factories
- Add helper methods: `build_empty()`, `build_partial()`, `build_valid()`
- Update docstrings for any alias relationships
- Ensure factories match updated model structure

#### 4.4 - Update tests for 100% coverage
After updating models and service, ensure tests cover:

**Model Tests (test_<model>_models.py):**
- [ ] All enum values
- [ ] Each model class instantiation (empty, minimal, full)
- [ ] All field validators (valid input, invalid input, edge cases)
- [ ] All serializers (each output format)
- [ ] ConfigDict extra="forbid" (test with unknown field)
- [ ] Default values
- [ ] Optional field handling (None, missing)
- [ ] Type coercion (string to list, etc.)
- [ ] Alias relationships (if CreateModel = UpdateModel)

**Service Tests (test_<model>.py):**
- [ ] get() - valid response, empty response, partial response, error response
- [ ] create() - valid data, empty data, invalid data, error
- [ ] update() - valid data, partial data, empty data, invalid data, error
- [ ] delete() - success, error
- [ ] Edge cases: unknown field formats, type coercion, enum handling
- [ ] Response parsing with model objects vs dicts

**Factory Tests:**
- Factories don't need separate tests; they're validated through model/service tests

### Phase 5: Verify 100% Coverage

Run pytest with coverage for the specific files (use dot notation for module paths):

```bash
poetry run pytest tests/scm/models/<category>/test_<model>_models.py \
                  tests/scm/config/<category>/test_<model>.py \
                  --cov=scm.models.<category>.<model> \
                  --cov=scm.config.<category>.<model> \
                  --cov-report=term-missing \
                  --cov-fail-under=100 \
                  -v
```

If coverage is below 100%:
1. Identify uncovered lines from the report
2. Add tests for those specific code paths
3. Re-run until 100% coverage achieved

### Phase 6: Final Summary

Provide a summary of all changes made:

```
## Changes Summary

### Model File (path)
- List of changes

### Service File (path)
- List of changes

### Test Files
- List of new/updated tests

### Coverage
- Final coverage percentage
- Number of tests passing
```

## Pydantic 2.0+ Reference

### ConfigDict Pattern
```python
from pydantic import BaseModel, ConfigDict

class MyModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )
```

### Field Validator Pattern
```python
from pydantic import field_validator

@field_validator("field_name", mode="before")
@classmethod
def validate_field(cls, v):
    if v is None:
        return []
    return v
```

### Field Serializer Pattern
```python
from pydantic import field_serializer

@field_serializer("field_name")
def serialize_field(self, value):
    if value is None:
        return None
    return value.model_dump()
```

### Model Validator Pattern
```python
from pydantic import model_validator

@model_validator(mode="after")
def validate_model(self) -> "MyModel":
    if not any([self.field1, self.field2]):
        raise ValueError("At least one field required")
    return self
```

## Important Notes

- ALWAYS read files before editing
- NEVER guess at file contents or structure
- Use TodoWrite to track progress through phases
- Ask user for confirmation before implementing changes
- Run tests after each significant change
- Ensure backwards compatibility with aliases
- Match OpenAPI spec exactly for field optionality
