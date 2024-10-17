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

### Example

```python
address_request = AddressRequestModel(
    name="test-address",
    fqdn="test.example.com",
    description="Sample address object",
    folder="Prisma Access",
)
```

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

### Example

```python
address_response = AddressResponseModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="test-address",
    fqdn="test.example.com",
    description="Sample address object",
    folder="Prisma Access",
)
```
