# Insights Models

## Overview

The Insights models provide structured data representations for the Prisma Access Insights API responses. These models ensure type safety, data validation, and consistent interfaces when working with alerts, metrics, and other telemetry data from your Prisma Access deployment.

## Available Models

### [Alert Models](alerts_models.md)
Data models for security and operational alerts:
- **Alert**: Complete alert data with severity, status, and metadata
- **AlertStatistic**: Statistical aggregation of alert data
- **AlertSeverity**: Constants for alert severity levels
- **AlertStatus**: Constants for alert status values

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

## Best Practices

1. **Type Safety**: Always use the provided models for type hints in your code
2. **Field Access**: Use model properties rather than dictionary access
3. **Validation**: Models automatically validate data on instantiation
4. **Serialization**: Use `model_dump()` to convert models to dictionaries
5. **Optional Fields**: Always check Optional fields before use

## Next Steps

- Review [Alert Models](alerts_models.md) for detailed alert data structures
- Check the [Alerts Configuration](../../insights/alerts.md) for usage examples
- See the main [SDK documentation](../../index.md) for general SDK patterns
