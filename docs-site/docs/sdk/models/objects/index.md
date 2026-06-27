# Objects Data Models

Pydantic models for validating and serializing object configuration resources in the Strata Cloud Manager SDK.

## Overview

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

### Creating an Object

```python
from scm.client import Scm
from scm.models.objects import AddressCreateModel, AddressUpdateModel

# Initialize client
client = Scm(
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
```

### Updating an Object

```python
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
