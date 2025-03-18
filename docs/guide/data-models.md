# Working with Data Models

The Strata Cloud Manager SDK uses Pydantic models to validate, structure, and manage data. Understanding these models will help you create and modify configuration objects correctly.

## Model Types

For each configuration object type, we typically provide several model classes:

### Base Models

Base models define the common attributes and validation rules for a configuration object type.

### Create Models

Create models define the structure and validation rules for creating new objects:

```python
from scm.models.objects.address import AddressCreateModel

# Create a model instance
address_data = AddressCreateModel(
    name="example-server",
    folder="Shared",
    ip_netmask="192.168.1.100/32",
    description="Example server created via SDK"
)

# Use the model to create an object
new_address = client.address.create(address_data.model_dump())
```

### Update Models

Update models define the structure and validation rules for updating existing objects:

```python
from scm.models.objects.address import AddressUpdateModel

# Create an update model instance
update_data = AddressUpdateModel(
    description="Updated description"
)

# Use the model to update an object
client.address.update(id="12345", data=update_data.model_dump())
```

### Response Models

Response models define the structure of data returned by the API:

```python
from scm.models.objects.address import AddressResponseModel

# Fetch an object and convert to a response model
address_dict = client.address.fetch(id="12345")
address = AddressResponseModel(**address_dict)

# Now you can access validated data with IDE completion
print(address.name)
print(address.ip_netmask)
```

## Using Models with the SDK

While the SDK methods accept dictionaries for convenience, using Pydantic models provides several advantages:

1. **Validation**: Models validate the data before sending it to the API
2. **Type hints**: Your IDE can provide completion for model attributes
3. **Documentation**: Models provide documentation for the data structure

Example using models:

```python
from scm import Scm
from scm.models.objects.address import AddressCreateModel, AddressResponseModel

# Initialize the client
client = Scm(client_id="...", client_secret="...", tenant_id="...")

# Create a model instance
address_data = AddressCreateModel(
    name="example-server",
    folder="Shared",
    ip_netmask="192.168.1.100/32"
)

# Create the object
new_address_dict = client.address.create(address_data.model_dump())
new_address = AddressResponseModel(**new_address_dict)

print(f"Created address: {new_address.name} with ID: {new_address.id}")
```

## Model Reference

For detailed information about specific models, check the model documentation:

- [Address Models](/sdk/models/objects/address_models.md)
- [Security Zone Models](/sdk/models/network/security_zone_models.md)
- [NAT Rule Models](/sdk/models/network/nat_rule_models.md)
- [Security Rule Models](/sdk/models/security_services/security_rule_models.md)

## Next Steps

- Explore [Operations](operations.md) to learn about candidate configurations and job monitoring
- Check out [Advanced Topics](advanced-topics.md) for pagination, filtering, and error handling