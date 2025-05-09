# Label Models

## Overview

The Label models provide a structured way to manage labels in Palo Alto Networks' Strata Cloud Manager.
These models handle validation of inputs and outputs when interacting with the SCM API.

## Attributes

| Attribute   | Type      | Required | Default | Description                                                    |
|-------------|-----------|----------|---------|----------------------------------------------------------------|
| name        | str       | Yes      | None    | Name of the label. Max length: 63 chars.                       |
| description | str       | No       | None    | Description of the label                                       |
| id          | UUID      | Yes*     | None    | UUID of the label (required only for update and response models)|

\* Only required for update and response models

## Exceptions

The Label models can raise the following exceptions during validation:

- **ValueError**: Raised when validation fails for any field, such as missing required fields or invalid formats

## Model Validators

The Label models utilize Pydantic validators to ensure data integrity:

- Name validation ensures the name meets length requirements
- Description validation ensures proper formatting if provided
- ID validation for update and response models

## Usage Examples

### Creating a Label Object

```python
# Using dictionary
from scm.config.setup import Label

label_dict = {
    "name": "environment",
    "description": "Environment classification label"
}

label_service = Label(api_client)
response = label_service.create(label_dict)

# Using model directly
from scm.models.setup import LabelCreateModel

label_obj = LabelCreateModel(
    name="environment",
    description="Environment classification label"
)

payload = label_obj.model_dump(exclude_unset=True)
response = label_service.create(payload)
```

### Updating a Label

```python
# Using dictionary
update_dict = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "environment-updated",
    "description": "Updated environment classification label"
}

response = label_service.update(update_dict)

# Using model directly
from scm.models.setup import LabelUpdateModel

update_label = LabelUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="environment-updated",
    description="Updated environment classification label"
)

payload = update_label.model_dump(exclude_unset=True)
response = label_service.update(payload)
```

## Model Hierarchy

The Label models follow a hierarchical structure:

- **LabelBaseModel**: Base model containing common attributes shared across all label models
  - **LabelCreateModel**: Extends base model for label creation operations
  - **LabelUpdateModel**: Extends base model with required ID field for updates
  - **LabelResponseModel**: Extends base model with fields specific to API responses

## Working with Label Models

### LabelBaseModel

The base model defines common attributes needed for all label operations:

```python
from scm.models.setup import LabelBaseModel

base = LabelBaseModel(
    name="environment",
    description="Environment label"
)
```

### LabelCreateModel

Used when creating new labels:

```python
from scm.models.setup import LabelCreateModel

create_model = LabelCreateModel(
    name="environment",
    description="Environment label"
)

# Convert to dictionary for API request
payload = create_model.model_dump(exclude_unset=True)
```

### LabelUpdateModel

Used when updating existing labels:

```python
from scm.models.setup import LabelUpdateModel

update_model = LabelUpdateModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="environment",
    description="Updated environment label"
)

# Convert to dictionary for API request
payload = update_model.model_dump(exclude_unset=True)
```

### LabelResponseModel

Represents labels returned from the API:

```python
from scm.models.setup import LabelResponseModel

# Typically constructed from API response
response_model = LabelResponseModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="environment",
    description="Environment label"
)

# Access attributes
print(f"Label ID: {response_model.id}")
print(f"Label Name: {response_model.name}")
print(f"Label Description: {response_model.description}")
```

## Best Practices

1. **Validation**: Leverage Pydantic model validation by using the models directly rather than raw dictionaries when possible.

2. **Type Checking**: Use type hints and the models' typing support to catch errors early in development.

3. **Excluding Unset Values**: When converting models to dictionaries, use `model_dump(exclude_unset=True)` to only include fields that have been explicitly set.

4. **Error Handling**: Wrap model creation in try/except blocks to catch and handle validation errors gracefully.

5. **Response Parsing**: Use the LabelResponseModel to parse API responses and access attributes in a type-safe manner.