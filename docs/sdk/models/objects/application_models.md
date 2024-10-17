# Application Models

This section covers the data models associated with the `Application` configuration object.

---

## ApplicationRequestModel

Used when creating or updating an application.

### Attributes

- `name` (str): **Required.** The name of the application.
- `category` (str): **Required.** The high-level category of the application.
- `subcategory` (str): **Required.** The specific subcategory.
- `technology` (str): **Required.** The underlying technology.
- `risk` (int): **Required.** The risk level (e.g., 1-5).
- `description` (Optional[str]): A description of the application.
- `ports` (Optional[List[str]]): List of ports associated with the application.
- **Container Type Fields** (Exactly one must be provided):
    - `folder` (Optional[str]): The folder where the application is defined.
    - `snippet` (Optional[str]): The snippet where the application is defined.
- **Boolean Attributes**:
    - `evasive` (Optional[bool])
    - `pervasive` (Optional[bool])
    - `excessive_bandwidth_use` (Optional[bool])
    - `used_by_malware` (Optional[bool])
    - `transfers_files` (Optional[bool])
    - `has_known_vulnerabilities` (Optional[bool])
    - `tunnels_other_apps` (Optional[bool])
    - `prone_to_misuse` (Optional[bool])
    - `no_certifications` (Optional[bool])

### Example

<div class="termy">

<!-- termynal -->

```python
application_request = ApplicationRequestModel(
    name="test-app",
    category="collaboration",
    subcategory="internet-conferencing",
    technology="client-server",
    risk=1,
    description="Sample application",
    ports=["tcp/80,443"],
    folder="Prisma Access",
    has_known_vulnerabilities=True,
)
```

</div>


---

## ApplicationResponseModel

Used when parsing applications retrieved from the API.

### Attributes

- `id` (str): The UUID of the application.
- `name` (str): The name of the application.
- `category` (str): The high-level category.
- `subcategory` (str): The specific subcategory.
- `technology` (str): The underlying technology.
- `risk` (int): The risk level.
- `description` (Optional[str]): A description of the application.
- `ports` (Optional[List[str]]): List of ports.
- **Container Type Fields**:
    - `folder` (Optional[str]): The folder where the application is defined.
    - `snippet` (Optional[str]): The snippet where the application is defined.
- **Boolean Attributes**:
    - `evasive` (Optional[bool])
    - `pervasive` (Optional[bool])
    - `excessive_bandwidth_use` (Optional[bool])
    - `used_by_malware` (Optional[bool])
    - `transfers_files` (Optional[bool])
    - `has_known_vulnerabilities` (Optional[bool])
    - `tunnels_other_apps` (Optional[bool])
    - `prone_to_misuse` (Optional[bool])
    - `no_certifications` (Optional[bool])

### Example

<div class="termy">

<!-- termynal -->

```python
application_response = ApplicationResponseModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="test-app",
    category="collaboration",
    subcategory="internet-conferencing",
    technology="client-server",
    risk=1,
    description="Sample application",
    ports=["tcp/80,443"],
    folder="Prisma Access",
    has_known_vulnerabilities=True,
)
```

</div>

