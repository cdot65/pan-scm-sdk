# Application Models

This section covers the data models associated with the `Application` configuration object.

---

## ApplicationRequestModel

Used when creating or updating an application.

### Attributes

- `name` (str): **Required.** The name of the application. Max length: 63 characters.
- `category` (str): **Required.** The high-level category of the application. Max length: 50 characters.
- `subcategory` (str): **Required.** The specific subcategory. Max length: 50 characters.
- `technology` (str): **Required.** The underlying technology. Max length: 50 characters.
- `risk` (int): **Required.** The risk level associated with the application.
- `description` (Optional[str]): A description of the application. Max length: 1023 characters.
- `ports` (Optional[List[str]]): List of ports associated with the application.
- **Container Type Fields** (Exactly one must be provided):
    - `folder` (Optional[str]): The folder where the application is defined. Max length: 64 characters.
    - `snippet` (Optional[str]): The snippet where the application is defined. Max length: 64 characters.
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

### Examples

1. Basic Application Request:

<div class="termy">

<!-- termynal -->

```python
application_request = ApplicationRequestModel(
    name="custom-app",
    category="business-systems",
    subcategory="database",
    technology="client-server",
    risk=3,
    folder="Custom Apps"
)
```

</div>

2. Detailed Application Request:

<div class="termy">

<!-- termynal -->

```python
application_request = ApplicationRequestModel(
    name="video-chat-app",
    category="collaboration",
    subcategory="video-conferencing",
    technology="browser-based",
    risk=2,
    description="Custom video conferencing application",
    ports=["tcp/8080", "udp/9000-9010"],
    folder="Collaboration Apps",
    evasive=False,
    pervasive=True,
    excessive_bandwidth_use=True,
    transfers_files=True,
    has_known_vulnerabilities=False
)
```

</div>

3. Application Request with Snippet:

<div class="termy">

<!-- termynal -->

```python
application_request = ApplicationRequestModel(
    name="legacy-app",
    category="business-systems",
    subcategory="erp",
    technology="client-server",
    risk=4,
    snippet="Legacy Apps",
    used_by_malware=False,
    no_certifications=True
)
```

</div>

---

## ApplicationResponseModel

Used when parsing applications retrieved from the API.

### Attributes

- `id` (UUID): The UUID of the application.
- `name` (str): The name of the application. Max length: 63 characters.
- `category` (str): The high-level category. Max length: 50 characters.
- `subcategory` (str): The specific subcategory. Max length: 50 characters.
- `technology` (str): The underlying technology. Max length: 50 characters.
- `risk` (int): The risk level associated with the application.
- `description` (Optional[str]): A description of the application. Max length: 1023 characters.
- `ports` (Optional[List[str]]): List of ports associated with the application.
- **Container Type Fields**:
    - `folder` (Optional[str]): The folder where the application is defined. Max length: 64 characters.
    - `snippet` (Optional[str]): The snippet where the application is defined. Max length: 64 characters.
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

### Examples

1. Basic Application Response:

<div class="termy">

<!-- termynal -->

```python
application_response = ApplicationResponseModel(
    id="123e4567-e89b-12d3-a456-426655440000",
    name="custom-app",
    category="business-systems",
    subcategory="database",
    technology="client-server",
    risk=3,
    folder="Custom Apps"
)
```

</div>

2. Detailed Application Response:

<div class="termy">

<!-- termynal -->

```python
application_response = ApplicationResponseModel(
    id="123e4567-e89b-12d3-a456-426655440001",
    name="video-chat-app",
    category="collaboration",
    subcategory="video-conferencing",
    technology="browser-based",
    risk=2,
    description="Custom video conferencing application",
    ports=["tcp/8080", "udp/9000-9010"],
    folder="Collaboration Apps",
    evasive=False,
    pervasive=True,
    excessive_bandwidth_use=True,
    transfers_files=True,
    has_known_vulnerabilities=False
)
```

</div>

3. Application Response with Snippet:

<div class="termy">

<!-- termynal -->

```python
application_response = ApplicationResponseModel(
    id="123e4567-e89b-12d3-a456-426655440002",
    name="legacy-app",
    category="business-systems",
    subcategory="erp",
    technology="client-server",
    risk=4,
    snippet="Legacy Apps",
    used_by_malware=False,
    no_certifications=True
)
```

</div>

---

## Full Example

Here's a comprehensive example demonstrating the usage of both `ApplicationRequestModel` and `ApplicationResponseModel`:

<div class="termy">

<!-- termynal -->

```python
from uuid import UUID
from scm.models.objects import ApplicationRequestModel, ApplicationResponseModel

# Create an ApplicationRequestModel
request_data = {
    "name": "advanced-collab-app",
    "category": "collaboration",
    "subcategory": "file-sharing",
    "technology": "cloud-based",
    "risk": 3,
    "description": "Advanced collaboration and file sharing application",
    "ports": ["tcp/443", "tcp/8443"],
    "folder": "Advanced Apps",
    "evasive": False,
    "pervasive": True,
    "excessive_bandwidth_use": False,
    "used_by_malware": False,
    "transfers_files": True,
    "has_known_vulnerabilities": False,
    "tunnels_other_apps": False,
    "prone_to_misuse": True,
    "no_certifications": False
}

app_request = ApplicationRequestModel(**request_data)
print(f"Application Request: {app_request}")

# Simulate API response
response_data = {
    "id": "123e4567-e89b-12d3-a456-426655440003",
    **request_data
}

# Create an ApplicationResponseModel
app_response = ApplicationResponseModel(**response_data)
print(f"Application Response: {app_response}")

# Access specific attributes
print(f"Application Name: {app_response.name}")
print(f"Risk Level: {app_response.risk}")
print(f"Folder: {app_response.folder}")
print(f"Transfers Files: {app_response.transfers_files}")
```

</div>

This example shows how to create both request and response models, demonstrating the full lifecycle of an application
object in the Strata Cloud Manager.
