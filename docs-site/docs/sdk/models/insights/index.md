# Insights Models

Data models for Prisma Access Insights API responses.

## Overview

The Insights models provide structured data representations for the Prisma Access Insights API responses. These models ensure type safety, data validation, and consistent interfaces when working with alerts, metrics, and other telemetry data from your Prisma Access deployment.

## Available Models

- [Alert Models](alerts_models.md) - Models for security and operational alerts

## Common Patterns

### Field Mapping

Many Insights models use field aliases to provide more intuitive property names:

```python
# API returns "alert_id", model exposes it as "id"
id: str = Field(None, alias="alert_id")

# API returns "message", model exposes it as "name"
name: Optional[str] = Field(None, alias="message")
```

### Flexible Response Handling

Insights models are designed to handle varying response formats:

```python
# Models use ConfigDict to allow additional fields
model_config = ConfigDict(extra="allow")

# This allows the model to accept and preserve additional fields
# that might be returned by the API in future versions
```

### JSON Field Parsing

Some fields may contain JSON strings that need parsing:

```python
@field_validator("metadata", mode="before")
def parse_json_string(cls, v):
    """Parse JSON string fields if needed."""
    if isinstance(v, str):
        import json
        try:
            return json.loads(v)
        except json.JSONDecodeError:
            return v
    return v
```

## Model Categories

### Response Models

These models represent data returned from the API:

- Read-only fields like `id`, `created_at`, etc.
- All fields from the resource
- Timestamp and metadata fields

### Statistic Models

These models represent aggregated data:

- Count fields
- Grouping fields (severity, category, state)
- Time-based aggregations

### Enum Classes

These provide constants for valid field values:

- Severity levels (Critical, High, Medium, Low, etc.)
- Status values (Raised, Cleared, etc.)
- Other categorical values

## Related Documentation

- [Alert Models](alerts_models.md) - Detailed alert data structures
- [Alerts Configuration](../../insights/alerts.md) - Usage examples
