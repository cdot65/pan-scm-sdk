# Address Models

This section covers the data models associated with the `Address` configuration object.

---

## AddressRequestModel

Used when creating or updating an address object.

### Attributes

- `name` (str): **Required.** The name of the address object.
- `description` (Optional[str]): A description of the address object.
- `tag` (Optional[List[str]]): Tags associated with the address object.
- **Address Type Fields** (Exactly one must be provided):
    - `ip_netmask` (Optional[str]): IP address with or without CIDR notation.
    - `ip_range` (Optional[str]): IP address range.
    - `ip_wildcard` (Optional[str]): IP wildcard mask.
    - `fqdn` (Optional[str]): Fully qualified domain name.
- **Container Type Fields** (Exactly one must be provided):
    - `folder` (Optional[str]): The folder where the address is defined.
    - `snippet` (Optional[str]): The snippet where the address is defined.
    - `device` (Optional[str]): The device where the address is defined.

### Examples

**Example 1: IP/Netmask Address**

<div class="termy">

<!-- termynal -->

```python
address_request = AddressRequestModel(
    name="internal_network",
    ip_netmask="192.168.1.0/24",
    description="Internal network address",
    folder="Shared",
    tag=["internal"]
)

# As a dictionary
address_dict = {
    "name": "internal_network",
    "ip_netmask": "192.168.1.0/24",
    "description": "Internal network address",
    "folder": "Shared",
    "tag": ["internal"]
}
```

</div>

**Example 2: FQDN Address**

<div class="termy">

<!-- termynal -->

```python
address_request = AddressRequestModel(
    name="example_website",
    fqdn="www.example.com",
    description="Example website address",
    folder="Prisma Access"
)

# As a dictionary
address_dict = {
    "name": "example_website",
    "fqdn": "www.example.com",
    "description": "Example website address",
    "folder": "Prisma Access"
}
```

</div>

**Example 3: IP Range Address**

<div class="termy">

<!-- termynal -->

```python
address_request = AddressRequestModel(
    name="dhcp_range",
    ip_range="10.0.0.100-10.0.0.200",
    description="DHCP address range",
    snippet="Network Config"
)

# As a dictionary
address_dict = {
    "name": "dhcp_range",
    "ip_range": "10.0.0.100-10.0.0.200",
    "description": "DHCP address range",
    "snippet": "Network Config"
}
```

</div>

---

## AddressResponseModel

Used when parsing address objects retrieved from the API.

### Attributes

- `id` (str): The UUID of the address object.
- `name` (str): The name of the address object.
- `description` (Optional[str]): A description of the address object.
- `tag` (Optional[List[str]]): Tags associated with the address object.
- **Address Type Fields**:
    - `ip_netmask` (Optional[str]): IP address with or without CIDR notation.
    - `ip_range` (Optional[str]): IP address range.
    - `ip_wildcard` (Optional[str]): IP wildcard mask.
    - `fqdn` (Optional[str]): Fully qualified domain name.
- **Container Type Fields**:
    - `folder` (Optional[str]): The folder where the address is defined.
    - `snippet` (Optional[str]): The snippet where the address is defined.
    - `device` (Optional[str]): The device where the address is defined.

### Examples

**Example 1: IP/Netmask Address Response**

<div class="termy">

<!-- termynal -->

```python
address_response = AddressResponseModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="internal_network",
    ip_netmask="192.168.1.0/24",
    description="Internal network address",
    folder="Shared",
    tag=["internal"]
)

# As a dictionary
address_dict = {
    "id": "123e4567-e89b-12d3-a456-426655440000",
    "name": "internal_network",
    "ip_netmask": "192.168.1.0/24",
    "description": "Internal network address",
    "folder": "Shared",
    "tag": ["internal"]
}
```

</div>

**Example 2: FQDN Address Response**

<div class="termy">

<!-- termynal -->

```python
address_response = AddressResponseModel(
    id="234e5678-f89c-23d4-b567-537766551111",
    name="example_website",
    fqdn="www.example.com",
    description="Example website address",
    folder="Prisma Access"
)

# As a dictionary
address_dict = {
    "id": "234e5678-f89c-23d4-b567-537766551111",
    "name": "example_website",
    "fqdn": "www.example.com",
    "description": "Example website address",
    "folder": "Prisma Access"
}
```

</div>

**Example 3: IP Range Address Response**

<div class="termy">

<!-- termynal -->

```python
address_response = AddressResponseModel(
    id="345e6789-g90d-34e5-c678-648877662222",
    name="dhcp_range",
    ip_range="10.0.0.100-10.0.0.200",
    description="DHCP address range",
    snippet="Network Config"
)

# As a dictionary
address_dict = {
    "id": "345e6789-g90d-34e5-c678-648877662222",
    "name": "dhcp_range",
    "ip_range": "10.0.0.100-10.0.0.200",
    "description": "DHCP address range",
    "snippet": "Network Config"
}
```

</div>

---

## Full Example: Creating and Using Address Models

Here's a complete example demonstrating how to create and use Address models:

<div class="termy">

<!-- termynal -->

```python
from scm.models.objects import AddressRequestModel, AddressResponseModel

# Create an AddressRequestModel
address_request = AddressRequestModel(
    name="corporate_network",
    ip_netmask="172.16.0.0/16",
    description="Corporate network address space",
    folder="Global",
    tag=["corporate", "internal"]
)

# Convert to dictionary for API request
address_dict = address_request.model_dump(exclude_unset=True)

# Simulate API response
api_response = {
    "id": "456f7890-h01e-45f6-d789-759988773333",
    "name": "corporate_network",
    "ip_netmask": "172.16.0.0/16",
    "description": "Corporate network address space",
    "folder": "Global",
    "tag": ["corporate", "internal"]
}

# Create an AddressResponseModel from API response
address_response = AddressResponseModel(**api_response)

# Use the response model
print(f"Address ID: {address_response.id}")
print(f"Address Name: {address_response.name}")
print(f"IP/Netmask: {address_response.ip_netmask}")
print(f"Description: {address_response.description}")
print(f"Folder: {address_response.folder}")
print(f"Tags: {', '.join(address_response.tag)}")
```

</div>

This example shows how to create an `AddressRequestModel`, convert it to a dictionary for an API request, and then
create an `AddressResponseModel` from a simulated API response. It demonstrates the full lifecycle of working with
Address models in the SDK.
