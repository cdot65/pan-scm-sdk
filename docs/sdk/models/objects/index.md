# Objects Data Models

## Table of Contents

1. [Overview](#overview)
2. [Model Types](#model-types)
3. [Common Model Patterns](#common-model-patterns)
4. [Usage Examples](#usage-examples)
5. [Models by Category](#models-by-category)
   1. [Address Objects](#address-objects)
   2. [Service Objects](#service-objects)
   3. [Application Objects](#application-objects)
   4. [Group Objects](#group-objects)
   5. [Profile Objects](#profile-objects)
   6. [Tag Objects](#tag-objects)
6. [Best Practices](#best-practices)
7. [Related Documentation](#related-documentation)

## Overview {#Overview}
<span id="overview"></span>

The Strata Cloud Manager SDK uses Pydantic models for data validation and serialization. These models ensure that the data being sent to and received from the Strata Cloud Manager API adheres to the expected structure and constraints. This section documents the models for object configuration resources.

## Model Types

For each configuration object, there are corresponding model types:

- **Create Models**: Used when creating new resources (`{Object}CreateModel`)
- **Update Models**: Used when updating existing resources (`{Object}UpdateModel`)
- **Response Models**: Used when parsing data retrieved from the API (`{Object}ResponseModel`)
- **Base Models**: Common shared attributes for related models (`{Object}BaseModel`)

## Common Model Patterns

Object models share common patterns:

- Container validation (exactly one of folder/snippet/device)
- UUID validation for identifiers
- String length and pattern validation
- Data type validation and conversion
- Tag normalization and validation
- Required field enforcement

## Usage Examples

```python
from scm.client import ScmClient
from scm.models.objects import AddressCreateModel, AddressUpdateModel

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a new object using a model
address = AddressCreateModel(
   name="web-server",
   description="Primary web server",
   ip_netmask="10.0.1.100/32",
   folder="Shared"
)

# Convert the model to a dictionary for the API call
address_dict = address.model_dump(exclude_unset=True)
result = client.address.create(address_dict)

# Update an existing object using a model
update_address = AddressUpdateModel(
   id=result.id,
   name="web-server-updated",
   description="Updated web server",
   ip_netmask="10.0.1.101/32",
   folder="Shared"
)

update_dict = update_address.model_dump(exclude_unset=True)
updated_result = client.address.update(update_dict)
```

## Models by Category

### Address Objects

- [Address Models](address_models.md) - IP addresses, ranges, FQDNs, and wildcards
- [Address Group Models](address_group_models.md) - Static and dynamic address groups

### Service Objects

- [Service Models](service_models.md) - Port and protocol definitions
- [Service Group Models](service_group_models.md) - Collections of services

### Application Objects

- [Application Models](application_models.md) - Custom application definitions
- [Application Filters Models](application_filters_models.md) - Application filtering criteria
- [Application Group Models](application_group_models.md) - Collections of applications

### Group Objects

- [Dynamic User Group Models](dynamic_user_group_models.md) - User group mapping
- [External Dynamic Lists Models](external_dynamic_lists_models.md) - External IP/URL/domain lists

### Profile Objects

- [HIP Object Models](hip_object_models.md) - Host Information Profile objects
- [HIP Profile Models](hip_profile_models.md) - Host Information Profiles
- [HTTP Server Profiles Models](http_server_profiles_models.md) - HTTP server configurations
- [Log Forwarding Profile Models](log_forwarding_profile_models.md) - Log forwarding configurations

### Tag Objects

- [Tag Models](tag_models.md) - Object categorization and organization tags

## Best Practices

1. **Model Validation**
   - Always validate input data with models before sending to the API
   - Handle validation errors appropriately
   - Use model_dump(exclude_unset=True) to avoid sending default values

2. **Container Consistency**
   - Maintain consistent container usage (folder/snippet/device)
   - Remember that exactly one container type must be specified
   - Use the same container type for related objects

3. **Model Conversion**
   - Convert API responses to response models for type safety
   - Use model_dump() for serialization to JSON or dictionaries
   - Leverage model validators for complex validation logic

4. **Error Handling**
   - Catch and handle ValueError exceptions from model validation
   - Implement proper error messages for validation failures
   - Validate model data before executing API calls

## Related Documentation

- [Object Configuration](../../config/objects/index.md) - Working with object configurations
- [Address Configuration](../../config/objects/address.md) - Address object operations
- [Service Configuration](../../config/objects/service.md) - Service object operations
