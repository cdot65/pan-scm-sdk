# Auto Tag Actions Models

This page describes the Pydantic models used for Auto Tag Actions configuration in the Strata Cloud Manager SDK.

## Overview

Auto Tag Actions models define the data structures for automated tag assignment based on traffic patterns, security events, and other triggers. These models handle attributes such as:

- Match criteria for when tags should be applied
- Action types (add/remove tags)
- Tag lists to apply
- Timeout durations for tag application
- Scope and filtering options

## Base Models

### AutoTagActionRequest

The base request model for creating or updating an auto tag action.

```python
class AutoTagActionRequest(BaseModel):
    name: str
    folder: str
    description: Optional[str] = None
    match_criteria: AutoTagMatchCriteria
    action: Literal["add", "remove"]
    tags: List[str]
    timeout: Optional[int] = None  # Duration in seconds
    scope: Optional[AutoTagScope] = None
    enabled: Optional[bool] = True
```

### AutoTagActionResponse

The response model for auto tag actions.

```python
class AutoTagActionResponse(BaseModel):
    id: str
    name: str
    folder: str
    description: Optional[str] = None
    match_criteria: AutoTagMatchCriteria
    action: Literal["add", "remove"]
    tags: List[TagResponse]
    timeout: Optional[int] = None
    scope: Optional[AutoTagScope] = None
    enabled: bool
    creation_time: datetime
    last_modified_time: datetime
    last_hit_time: Optional[datetime] = None
    hit_count: Optional[int] = None
```

## Match Criteria Models

Models for defining when auto tag actions should be triggered.

### AutoTagMatchCriteria

```python
class AutoTagMatchCriteria(BaseModel):
    # Common filters
    source_address: Optional[List[str]] = None
    destination_address: Optional[List[str]] = None
    source_user: Optional[List[str]] = None
    source_zone: Optional[List[str]] = None
    destination_zone: Optional[List[str]] = None
    
    # Security event criteria
    severity: Optional[Union[str, List[str]]] = None
    threat_name: Optional[str] = None
    threat_id: Optional[str] = None
    threat_type: Optional[List[str]] = None
    action_taken: Optional[str] = None
    
    # Application criteria
    application: Optional[AutoTagApplicationCriteria] = None
    
    # URL/Domain criteria
    url_category: Optional[List[str]] = None
    destination: Optional[AutoTagDestinationCriteria] = None
    
    # Data patterns
    data_pattern: Optional[List[str]] = None
    
    # Custom criteria
    custom_criteria: Optional[Dict[str, Any]] = None
```

### AutoTagApplicationCriteria

```python
class AutoTagApplicationCriteria(BaseModel):
    name: Optional[List[str]] = None
    category: Optional[List[str]] = None
    technology: Optional[List[str]] = None
    risk: Optional[List[int]] = None  # 1-5 risk levels
    characteristic: Optional[List[str]] = None
    tag: Optional[List[str]] = None
```

### AutoTagDestinationCriteria

```python
class AutoTagDestinationCriteria(BaseModel):
    region: Optional[List[str]] = None
    country: Optional[List[str]] = None
    domain: Optional[str] = None
    domain_contains: Optional[List[str]] = None
```

## Scope Models

Models for defining the scope of auto tag actions.

### AutoTagScope

```python
class AutoTagScope(BaseModel):
    device_groups: Optional[List[str]] = None
    devices: Optional[List[str]] = None
    vsys: Optional[List[str]] = None
    apply_to: Optional[Literal["source", "destination", "both"]] = "source"
```

## Tag Models

Models for tag references in auto tag actions.

### TagReference

```python
class TagReference(BaseModel):
    name: str
    id: Optional[str] = None
```

### TagResponse

```python
class TagResponse(BaseModel):
    id: str
    name: str
    color: Optional[str] = None
```

## List Models

Models for paginated list responses.

### AutoTagActionListResponse

```python
class AutoTagActionListResponse(BaseModel):
    data: List[AutoTagActionResponse]
    count: int
    total: int
    limit: Optional[int] = None
    offset: Optional[int] = None
```

## Usage Examples

### Creating Auto Tag Action Request

```python
from scm.models.objects.auto_tag_actions import (
    AutoTagActionRequest,
    AutoTagMatchCriteria,
    AutoTagApplicationCriteria
)

# Define application criteria
app_criteria = AutoTagApplicationCriteria(
    risk=[4, 5],  # High and critical risk
    category=["peer-to-peer", "proxies"]
)

# Define match criteria
match_criteria = AutoTagMatchCriteria(
    application=app_criteria,
    source_zone=["trust"],
    destination_zone=["untrust"]
)

# Create auto tag action request
auto_tag_request = AutoTagActionRequest(
    name="high-risk-app-users",
    folder="Texas",
    description="Tag users of high-risk applications",
    match_criteria=match_criteria,
    action="add",
    tags=["high-risk-user", "excessive-p2p"],
    timeout=86400  # 24 hours
)

# Use the model with the SDK
client.auto_tag_actions.create(auto_tag_request)
```

### Parsing Auto Tag Action Response

```python
from scm.models.objects.auto_tag_actions import AutoTagActionResponse

# Parse API response into Auto Tag Action model
auto_tag_response = AutoTagActionResponse.parse_obj(api_response_json)

# Access model attributes
print(f"Auto Tag Action: {auto_tag_response.name}")
print(f"Action: {auto_tag_response.action}")

# Process tags
for tag in auto_tag_response.tags:
    print(f"Tag: {tag.name} (ID: {tag.id})")

# Check match criteria
if auto_tag_response.match_criteria.application:
    app_criteria = auto_tag_response.match_criteria.application
    if app_criteria.risk:
        print(f"Risk levels: {app_criteria.risk}")
    if app_criteria.category:
        print(f"Categories: {app_criteria.category}")
```