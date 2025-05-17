# SDK Service File Styling Conventions

This document defines the required conventions and standards for all SDK service files (e.g., `scm/config/objects/address.py`) in the `pan-scm-sdk` project. Adhering to these standards ensures code quality, maintainability, and a consistent developer experience.

---

## 1. File & Class Structure

- **One main service class per file**, named after the resource (PascalCase, singular).
- **Header docstring**: Google-style, describing the file's purpose and resource.
- **Imports**:
  - Standard library imports first (e.g., `logging`, `typing`).
  - SDK-internal modules next (absolute imports only).
  - Models and exceptions last.
- **Class-level constants**: `ENDPOINT`, `DEFAULT_MAX_LIMIT`, `ABSOLUTE_MAX_LIMIT`.
- **Constructor (`__init__`)**: Accepts `api_client`, `max_limit`; sets up logger and validates limit.
- **`max_limit` property**: With getter and setter, both documented.
- **Private `_validate_max_limit` method**: Validates input and raises `InvalidObjectError` with detailed messages.
- **CRUD methods**: At minimum, `create`, `get`, `update`, all returning a Pydantic ResponseModel and fully type-annotated.
- **Static `_apply_filters` method**: For client-side filtering, with type hints and docstrings.

## 2. Naming & Typing

- **snake_case** for all methods, properties, and variables.
- **PascalCase** for classes and Pydantic models.
- **UPPER_CASE** for constants.
- **Type hints**: Required for all parameters and return values (Python 3.10+).
- **Pydantic V2 models**: Used for all resource data.

## 3. Docstrings & Comments

- **Google-style docstrings**: Required for all public classes and methods, including argument, return, and exception details.
- **Inline comments**: Used for clarity, especially for validation and API workflows.

## 4. Formatting & Linting

- **Line length**: 88 characters (ruff default).
- **Blank lines**: Between class-level constants, methods, and logical blocks.
- **Ruff**: Used for linting/formatting, with isort for imports (see `pyproject.toml`).
- **Absolute imports**: Required for all SDK-internal modules.

## 5. Logic & Workflow

- **Input validation**: All user inputs (esp. limits, enums) are validated, with custom exceptions raised.
- **Model-driven**: All data validated/serialized via Pydantic models.
- **API calls**: Always via `self.api_client`, with endpoint and params explicit.
- **Error handling**: Always uses SDK custom exceptions, detailed error codes/messages.

## 6. Special Behaviors

- **Boolean field handling**: Only include `True` values in payloads for SCM API (omit `False`).
- **Serialization**: Always use `.model_dump(exclude_unset=True)` for payloads.

## 7. Example Skeleton

```python
"""<Resource> configuration service for Strata Cloud Manager SDK.

Provides service class for managing <resource> objects via the SCM API.
"""

import logging
from typing import Any, Dict, List, Optional

from scm.config import BaseObject
from scm.exceptions import InvalidObjectError
from scm.models.<category> import <Resource>CreateModel, <Resource>UpdateModel, <Resource>ResponseModel

class <Resource>(BaseObject):
    """Manages <Resource> objects in Palo Alto Networks' Strata Cloud Manager.

    Args:
        api_client: The API client instance
        max_limit (Optional[int]): Maximum number of objects to return in a single API request.

    """

    ENDPOINT = "/config/<category>/v1/<resource>s"
    DEFAULT_MAX_LIMIT = 2500
    ABSOLUTE_MAX_LIMIT = 5000

    def __init__(self, api_client, max_limit: Optional[int] = None):
        """Initialize the <Resource> service with the given API client."""
        super().__init__(api_client)
        self.logger = logging.getLogger(__name__)
        self._max_limit = self._validate_max_limit(max_limit)

    @property
    def max_limit(self) -> int:
        """Get the current maximum limit for API requests."""
        return self._max_limit

    @max_limit.setter
    def max_limit(self, value: int) -> None:
        """Set a new maximum limit for API requests."""
        self._max_limit = self._validate_max_limit(value)

    def _validate_max_limit(self, limit: Optional[int]) -> int:
        """Validate the max_limit parameter.

        Args:
            limit: The limit to validate
        Returns:
            int: The validated limit
        Raises:
            InvalidObjectError: If the limit is invalid
        """
        # ...implementation...

    def create(self, data: Dict[str, Any]) -> <Resource>ResponseModel:
        """Create a new <resource> object.
        Returns:
            <Resource>ResponseModel
        """
        # ...implementation...

    def get(self, object_id: str) -> <Resource>ResponseModel:
        """Get a <resource> object by ID.
        Returns:
            <Resource>ResponseModel
        """
        # ...implementation...

    def update(self, <resource>: <Resource>UpdateModel) -> <Resource>ResponseModel:
        """Update an existing <resource> object.
        Args:
            <resource>: <Resource>UpdateModel instance containing the update data
        Returns:
            <Resource>ResponseModel
        """
        # ...implementation...

    @staticmethod
    def _apply_filters(<resources>: List[<Resource>ResponseModel], filters: Dict[str, Any]) -> List[<Resource>ResponseModel]:
        """Apply client-side filtering to the list of <resource> objects.
        Args:
            <resources>: List of <Resource>ResponseModel objects
            filters: Dictionary of filter criteria
        Returns:
            List[<Resource>ResponseModel]: Filtered list of <resource> objects
        """
        # ...implementation...
```

---

For questions or updates, see `.windsurfrules` or contact the maintainers.
