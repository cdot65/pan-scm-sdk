# Setup Data Models

## Overview

The Setup models provide structured data representations for resources related to organization and environment setup in
Palo Alto Networks' Strata Cloud Manager. These models are used to validate, serialize, and deserialize data for API
operations.

## Available Setup Models

| Model                               | Description                                                |
|-------------------------------------|------------------------------------------------------------|
| [Folder Models](folder_models.md)   | Models for folder creation, updates, and responses         |
| [Label Models](label_models.md)     | Models for label creation, updates, and responses          |
| [Snippet Models](snippet_models.md) | Models for snippet operations and responses                |
| [Device Models](device_models.md)   | Pydantic models for device resources and licenses          |
| [Variable Models](variable_models.md) | Models for typed variables with container validation     |

## Working with Setup Models

Setup models provide a structured way to interact with the Strata Cloud Manager API. They ensure data validation before
requests are sent and proper parsing of API responses.

### Variable Models

The Variable models include:

- **VariableBaseModel**: Base model with common fields for all variable operations
- **VariableCreateModel**: Model for creating new variables, with container validation
- **VariableUpdateModel**: Model for updating existing variables
- **VariableResponseModel**: Model representing API responses for variables

These models handle validation for:
- Variable type validation (18 supported types)
- Container validation (ensuring exactly one of folder, snippet, or device is specified)
- Additional fields for filtering (labels, parent, snippets, etc.)

For complete details on specific models, refer to the corresponding model documentation pages listed above.
