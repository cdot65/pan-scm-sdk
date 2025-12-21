I'll create a comprehensive style guide based on the provided mkdocs files, capturing the structure, styling, and design patterns for future documentation.

# Palo Alto Networks Strata Cloud Manager Documentation Style Guide

## Document Structure

1. **Title and Header**
   - Use H1 (`#`) for the main document title
   - Title should clearly indicate the object/component being documented
   - Format: "[Object] Configuration Object"

2. **Table of Contents**
   - Include a structured ToC immediately after the title
   - Use numbered lists for ToC items
   - Include anchor links to each section (`[Section Name](#section-name)`)
   - Standard sections should appear in this order:
     1. Overview
     2. Core Methods
     3. Model Attributes
     4. Exceptions
     5. Basic Configuration
     6. Usage Examples (with sub-sections)
     7. Managing Configuration Changes
     8. Error Handling
     9. Best Practices
     10. Full Script Examples
     11. Related Models

3. **Section Headers**
   - Use H2 (`##`) for main sections
   - Use H3 (`###`) for subsections
   - Keep section headers concise and descriptive
   - Use title case for all headings

## Content Elements

### Overview Section
- Provide a concise introduction to the object/component
- Explain its purpose and relationship to other components
- Mention base classes or inheritance where applicable
- Keep to 2-4 sentences

### Method and Attribute Tables
- Use markdown tables for structured information
- Include headers with proper alignment
- Common table columns for methods:
  - Method
  - Description
  - Parameters
  - Return Type
- Common table columns for attributes:
  - Attribute
  - Type
  - Required
  - Description
- Use consistent formatting for all tables
- Include asterisks (*) to indicate special conditions

### Exception Tables
- Document all possible exceptions
- Include HTTP code and description columns
- Group related exceptions together

### Code Examples

1. **Code Blocks**
   - Use triple backtick code blocks with language specification
   ```
   ```python
   # Code goes here
   ```
   ```

2. **Import Statements**
   - Show proper import structure at the beginning of examples
   - Demonstrate both unified client interface and traditional approach where applicable

3. **Client Initialization**
   - Include standard client initialization for all example blocks
   - Use placeholder values (`your_client_id`, `your_client_secret`, `your_tsg_id`)

4. **Code Comments**
   - Include descriptive comments for significant operations
   - Use comments to explain the purpose of each code block
   - Include print statements for result validation

5. **Error Handling**
   - Show comprehensive try/except blocks in error handling examples
   - Include specific exception handling for all relevant exceptions
   - Add message logging in the exception handlers

### Notes and Admonitions
- Use !!! note syntax for important information
- Keep notes concise and focused
- Use notes to highlight best practices or alternative approaches

## Styling Guidelines

1. **Terminology**
   - Use consistent terminology throughout documentation
   - Prefer "unified client interface" when referring to the modern approach
   - Use "traditional service instantiation" for the legacy approach
   - Be consistent with capitalization (e.g., "Strata Cloud Manager" not "strata cloud manager")

2. **Code Style**
   - Follow PEP 8 conventions for Python code
   - Use 3-space indentation in examples for readability
   - Use snake_case for variables and function names
   - Include proper spacing around operators

3. **Naming Conventions**
   - Use descriptive variable names that indicate their purpose
   - Follow consistent naming patterns across examples:
     - `client` for client instances
     - `[object]_config` for configuration dictionaries
     - `new_[object]` for newly created objects
     - `existing_[object]` for objects being modified
     - `updated_[object]` for objects after update

4. **Example Structure**
   - Each code example should follow this pattern:
     1. Start with imports and initialization
     2. Show the main operation with comments
     3. Demonstrate result handling or validation
   - Group related operations into single examples
   - Provide both simple and complex examples

## Section-Specific Guidelines

### Basic Configuration
- Show both unified client interface and traditional service instantiation
- Clearly mark the recommended approach
- Include a note about which approach is preferred

### Usage Examples
- Break down by operation type (create, retrieve, update, list, delete)
- Show complete examples including imports and initialization
- Demonstrate different variations where applicable (static vs. dynamic for address groups)
- Include parameter variations and filtering options

### Managing Configuration Changes
- Show commit operations with proper parameters
- Include job monitoring examples
- Demonstrate sync and async approaches

### Best Practices
- Use numbered lists for best practice categories
- Group related best practices
- Include 4-6 items per category
- Cover client usage, performance, security, and object-specific considerations

### Related Models
- Link to corresponding model documentation
- List all related model types with links

## Example Templates

For consistency, use these templates for common documentation patterns:

### Method Table Template
```markdown
## Core Methods

| Method     | Description                | Parameters                | Return Type            |
|------------|----------------------------|---------------------------|------------------------|
| `create()` | Creates a new object       | `data: Dict[str, Any]`    | `ResponseModel`        |
| `get()`    | Retrieves object by ID     | `object_id: str`          | `ResponseModel`        |
| `update()` | Updates an existing object | `object: UpdateModel`     | `ResponseModel`        |
| `delete()` | Deletes an object          | `object_id: str`          | `None`                 |
| `list()`   | Lists objects with filters | `folder: str`, `**filters`| `List[ResponseModel]`  |
```

### Code Example Template
```markdown
```python
from scm.client import ScmClient

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create configuration
config = {
   "name": "example_name",
   # Additional parameters
   "folder": "Texas"
}

# Perform operation
result = client.service.operation(config)

# Process results
print(f"Operation result: {result.id}")
```
```

### Error Handling Template
```markdown
```python
from scm.client import ScmClient
from scm.exceptions import (
   ExceptionType1,
   ExceptionType2
)

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

try:
   # Operation code
   result = client.service.operation(config)

except ExceptionType1 as e:
   print(f"Error message: {e.message}")
except ExceptionType2 as e:
   print(f"Error message: {e.message}")
```
```

## Pydantic Model Guidelines

### Model Validators

When using `@model_validator(mode="after")`, always use instance methods (with `self`), not classmethods (with `cls`):

```python
# ✅ Correct - instance method
@model_validator(mode="after")
def validate_container_type(self) -> "MyCreateModel":
    """Validate that exactly one container type is provided."""
    container_fields = ["folder", "snippet", "device"]
    provided = [f for f in container_fields if getattr(self, f) is not None]
    if len(provided) != 1:
        raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
    return self

# ❌ Deprecated - classmethod pattern (removed in Pydantic v3)
@model_validator(mode="after")
def validate_container_type(cls, values):  # Don't use this pattern
    ...
    return values
```

This pattern was deprecated in Pydantic v2.12 and will be removed in v3.0.

### Field Validators

Field validators using `@field_validator` should continue using `cls` as the first parameter:

```python
@field_validator("name")
def validate_name(cls, v):
    """Validate name format."""
    if not v:
        raise ValueError("Name cannot be empty")
    return v
```

### Model Configuration

Always use `ConfigDict` for model configuration:

```python
from pydantic import BaseModel, ConfigDict

class MyModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        populate_by_name=True,
        validate_assignment=True,
    )
```

## Final Recommendations

1. **Consistency** - Maintain consistent formatting, terminology, and structure across all documentation
2. **Completeness** - Ensure all methods, attributes, and exceptions are fully documented
3. **Examples** - Provide comprehensive examples for all common operations
4. **Error Handling** - Include proper error handling in all examples
5. **Navigation** - Ensure proper linking between related documentation pages
6. **Readability** - Use clear, concise language and proper code formatting

This style guide captures the consistent patterns observed in the provided documentation and should serve as a comprehensive reference for creating future mkdocs pages that maintain the same professional look and feel.
