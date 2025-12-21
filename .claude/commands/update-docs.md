# Update Documentation Command

Update MkDocs documentation pages by comparing against source code to identify gaps and inconsistencies.

## Arguments

- `$1` - MkDocs page for SDK configuration class (e.g., `docs/sdk/config/objects/address.md`)
- `$2` - MkDocs page for Pydantic data model (e.g., `docs/sdk/models/objects/address_models.md`)
- `$3` - SDK configuration class file (e.g., `scm/config/objects/address.py`)
- `$4` - Pydantic data model file (e.g., `scm/models/objects/address.py`)

## Workflow

Execute phases in order. Use TodoWrite to track progress.

### Phase 1: Read Source Code

#### Step 1.1 - Read SDK Configuration Class ($3)

Read and identify:

- Class name and inheritance
- ENDPOINT constant
- CRUD methods (create, get, update, delete, list, fetch)
- Method signatures and parameters
- Filter parameters supported by list()
- Return types for each method
- Container validation (folder/snippet/device)
- Pagination handling (max_limit)
- Any special processing or transformations

#### Step 1.2 - Read Pydantic Data Model ($4)

Read and identify:

- All model classes (Base, Create, Update, Response)
- All Enum classes with their values
- Field definitions (name, type, required/optional, defaults)
- Field constraints (max_length, pattern, etc.)
- Validators (@field_validator, @model_validator)
- Serializers (@field_serializer)
- Container validation logic
- Type-specific validation (e.g., exactly one of multiple fields required)

### Phase 2: Read Existing Documentation

#### Step 2.1 - Read Config Class Doc ($1)

Read and note current state of:

- Overview section
- Core Methods table
- Model Attributes table
- Exceptions table
- Basic Configuration section
- Usage Examples (create, get, update, delete, list, fetch)
- Filtering Responses section
- Pagination section
- Managing Configuration Changes section
- Error Handling section
- Best Practices section
- Full Script Examples
- Related Models links

#### Step 2.2 - Read Model Doc ($2)

Read and note current state of:

- Overview section
- Attributes table
- Exceptions section
- Model Validators section
- Usage Examples

### Phase 3: Identify Gaps and Inconsistencies

Compare source code against documentation:

#### 3.1 - Config Class Doc Gaps

| Check | What to Compare |
|-------|-----------------|
| Methods | All CRUD methods in class vs documented methods |
| Parameters | Method params in code vs documented params |
| Return types | Code return types vs documented return types |
| Filter params | list() filters in code vs documented filters |
| Exceptions | Raised exceptions vs documented exceptions |
| Examples | Examples match current API patterns |

#### 3.2 - Model Doc Gaps

| Check | What to Compare |
|-------|-----------------|
| Models | All model classes vs documented |
| Fields | All fields per model vs documented fields |
| Types | Field types in code vs documented types |
| Required | Required fields in code vs documented required |
| Defaults | Default values in code vs documented defaults |
| Constraints | Constraints (maxLength, pattern) vs documented |
| Validators | All validators vs documented validators |
| Enums | All enum values vs documented |

#### 3.3 - Cross-Document Consistency

- Attributes in config doc match model doc
- Return types reference correct model names
- Related Models links are valid
- Import paths are correct

### Phase 4: Report Findings

Present a structured report of gaps and inconsistencies:

```markdown
## Documentation Analysis

### Config Class Doc ($1)

#### Missing
- [ ] Item description

#### Outdated
- [ ] Item with current vs documented value

#### Inconsistent
- [ ] Item with inconsistency description

### Model Doc ($2)

#### Missing
- [ ] Item description

#### Outdated
- [ ] Item with current vs documented value

#### Inconsistent
- [ ] Item with inconsistency description
```

Ask user for confirmation before proceeding to updates.

### Phase 5: Update Documentation

After user approval, make updates:

#### 5.1 - Update Config Class Doc ($1)

- Update Core Methods table
- Update Model Attributes table
- Update Exceptions table
- Update/add usage examples
- Update filter parameters
- Fix any import paths
- Update Related Models links

#### 5.2 - Update Model Doc ($2)

- Update Overview if needed
- Update Attributes table
- Update Exceptions section
- Add/update validators documentation
- Update usage examples
- Document all enum values

### Phase 6: Final Summary

```markdown
## Changes Summary

### Config Class Doc ($1)
- List of changes made

### Model Doc ($2)
- List of changes made

### Unresolved
- Any items that couldn't be updated with reasons
```

## Documentation Patterns

### Core Methods Table Format

```markdown
| Method     | Description                | Parameters              | Return Type          |
|------------|----------------------------|-------------------------|----------------------|
| `create()` | Creates a new object       | `data: Dict[str, Any]`  | `ResourceResponse`   |
```

### Attributes Table Format

```markdown
| Attribute | Type      | Required | Default | Description                              |
|-----------|-----------|----------|---------|------------------------------------------|
| name      | str       | Yes      | None    | Name of object. Max length: 63 chars     |
```

### Exceptions Table Format

```markdown
| Exception              | HTTP Code | Description              |
|------------------------|-----------|--------------------------|
| `InvalidObjectError`   | 400       | Invalid data or format   |
```

### Usage Example Pattern (Unified Client)

```python
from scm.client import ScmClient

client = ScmClient(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id"
)

# Access service through client
result = client.resource_name.method(params)
```

### Update Example Pattern (Preferred)

Always show the fetch → dot update → update workflow. Do NOT import Pydantic models for updates.

```python
# Fetch existing object
existing = client.resource_name.fetch(name="object_name", folder="Texas")

# Modify attributes using dot notation
existing.description = "Updated description"
existing.some_field = "new_value"

# Pass modified object to update()
updated = client.resource_name.update(existing)
```

## Important Notes

- ALWAYS read files before editing
- Preserve existing valid content; only update outdated/missing parts
- Use consistent formatting matching existing docs
- Keep examples practical and working
- Ensure all code examples use unified client interface pattern
- Update examples must use fetch → dot notation → update workflow (never import Pydantic models for updates)
- Reference correct model names in return types
- Validate markdown renders correctly
