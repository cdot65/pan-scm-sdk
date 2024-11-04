# DNS Security Profile Configuration Object

The `DNSSecurityProfile` class is used to manage DNS Security Profile objects in the Strata Cloud Manager.
It provides methods to create, retrieve, update, delete, and list DNS Security Profile objects.

---

## Creating an API client object

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm

api_client = Scm(
    client_id="this-is-a-placeholder",
    client_secret="this-is-a-placeholder",
    tsg_id="this-is-a-placeholder",
)
```

</div>

---

## Importing the DNSSecurityProfile Class

<div class="termy">

<!-- termynal -->

```python
from scm.config.security import DNSSecurityProfile

dns_security_profile = DNSSecurityProfile(api_client)
```

</div>

## Methods

### `create(data: Dict[str, Any]) -> DNSSecurityProfileResponseModelModel`

Creates a new DNS Security Profile object.

**Parameters:**

- `data` (Dict[str, Any]): A dictionary containing the DNS Security Profile object data.

**Example:**

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "test_profile",
    "description": "Created via pan-scm-sdk",
    "folder": "Shared",
    "botnet_domains": {
        "dns_security_categories": [
            {
                "name": "grayware",
                "action": "block",
                "log_level": "medium",
                "packet_capture": "single-packet"
            }
        ],
        "lists": [
            {
                "name": "custom_list",
                "action": {"block": {}},
                "packet_capture": "disable"
            }
        ],
        "sinkhole": {
            "ipv4_address": "pan-sinkhole-default-ip",
            "ipv6_address": "::1"
        },
        "whitelist": [
            {
                "name": "example.com",
                "description": "Whitelisted domain"
            }
        ]
    }
}

new_profile = dns_security_profile.create(profile_data)
print(f"Created DNS Security Profile with ID: {new_profile.id}")
```

</div>

### `get(object_id: str) -> DNSSecurityProfileResponseModelModel`

Retrieves a DNS Security Profile object by its ID.

**Parameters:**

- `object_id` (str): The UUID of the DNS Security Profile object.

**Example:**

<div class="termy">

<!-- termynal -->

```python
profile_id = "12345678-1234-1234-1234-123456789012"
profile_object = dns_security_profile.get(profile_id)
print(f"Profile Name: {profile_object.name}")
```

</div>

### `update(object_id: str, data: Dict[str, Any]) -> DNSSecurityProfileResponseModelModel`

Updates an existing DNS Security Profile object.

**Parameters:**

- `object_id` (str): The UUID of the DNS Security Profile object.
- `data` (Dict[str, Any]): A dictionary containing the updated DNS Security Profile data.

**Example:**

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "name": "updated_profile",
    "description": "Updated via pan-scm-sdk",
    "folder": "Shared",
    "botnet_domains": {
        "dns_security_categories": [
            {
                "name": "malware",
                "action": "sinkhole",
                "log_level": "high",
                "packet_capture": "extended-capture"
            }
        ]
    }
}

updated_profile = dns_security_profile.update(profile_id, update_data)
print(f"Updated DNS Security Profile with ID: {updated_profile.id}")
```

</div>

### `delete(object_id: str) -> None`

Deletes a DNS Security Profile object by its ID.

**Parameters:**

- `object_id` (str): The UUID of the DNS Security Profile object.

**Example:**

<div class="termy">

<!-- termynal -->

```python
dns_security_profile.delete(profile_id)
print(f"Deleted DNS Security Profile with ID: {profile_id}")
```

</div>

###

`list(folder: Optional[str] = None, snippet: Optional[str] = None, device: Optional[str] = None, offset: Optional[int] = None, limit: Optional[int] = None, name: Optional[str] = None, **filters) -> List[DNSSecurityProfileResponseModelModel]`

Lists DNS Security Profile objects, optionally filtered by folder, snippet, device, or other criteria.

**Parameters:**

- `folder` (Optional[str]): The folder to list profiles from.
- `snippet` (Optional[str]): The snippet to list profiles from.
- `device` (Optional[str]): The device to list profiles from.
- `offset` (Optional[int]): The pagination offset.
- `limit` (Optional[int]): The pagination limit.
- `name` (Optional[str]): Filter profiles by name.
- `**filters`: Additional filters.

**Example:**

<div class="termy">

<!-- termynal -->

```python
profiles = dns_security_profile.list(folder='Shared', limit=10)

for profile in profiles:
    print(f"Profile Name: {profile.name}, ID: {profile.id}")
```

</div>

---

## Usage Examples

### Example 1: Creating a DNS Security Profile with Custom Lists

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "custom_list_profile",
    "description": "Profile with custom lists",
    "folder": "Shared",
    "botnet_domains": {
        "lists": [
            {
                "name": "custom_blocklist",
                "action": {"block": {}},
                "packet_capture": "single-packet"
            },
            {
                "name": "custom_allowlist",
                "action": {"allow": {}},
                "packet_capture": "disable"
            }
        ]
    }
}

new_profile = dns_security_profile.create(profile_data)
print(f"Created profile: {new_profile.name} with ID: {new_profile.id}")
```

</div>

### Example 2: Updating a DNS Security Profile with Sinkhole Settings

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "botnet_domains": {
        "sinkhole": {
            "ipv4_address": "127.0.0.1",
            "ipv6_address": "::1"
        }
    }
}

updated_profile = dns_security_profile.update(new_profile.id, update_data)
print(f"Updated profile: {updated_profile.name}")
```

</div>

### Example 3: Creating a Profile with DNS Security Categories

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "category_profile",
    "folder": "Shared",
    "botnet_domains": {
        "dns_security_categories": [
            {
                "name": "grayware",
                "action": "alert",
                "log_level": "informational"
            },
            {
                "name": "malware",
                "action": "block",
                "log_level": "critical",
                "packet_capture": "extended-capture"
            }
        ]
    }
}

new_profile = dns_security_profile.create(profile_data)
print(f"Created profile with categories: {new_profile.name}")
```

</div>

### Example 4: Listing DNS Security Profiles with Filters

<div class="termy">

<!-- termynal -->

```python
profiles = dns_security_profile.list(
    folder='Shared',
    limit=5,
    name='custom'
)

for profile in profiles:
    print(f"Profile: {profile.name}, Description: {profile.description}")
```

</div>

### Example 5: Creating a Profile with Whitelist Entries

<div class="termy">

<!-- termynal -->

```python
profile_data = {
    "name": "whitelist_profile",
    "folder": "Shared",
    "botnet_domains": {
        "whitelist": [
            {
                "name": "example.com",
                "description": "Trusted domain"
            },
            {
                "name": "safedomain.org",
                "description": "Another trusted domain"
            }
        ]
    }
}

new_profile = dns_security_profile.create(profile_data)
print(f"Created profile with whitelist: {new_profile.name}")
```

</div>

### Example 6: Updating a Profile with Multiple Components

<div class="termy">

<!-- termynal -->

```python
update_data = {
    "description": "Comprehensive DNS Security Profile",
    "botnet_domains": {
        "dns_security_categories": [
            {
                "name": "phishing",
                "action": "block",
                "log_level": "high"
            }
        ],
        "lists": [
            {
                "name": "custom_blocklist",
                "action": {"sinkhole": {}},
                "packet_capture": "single-packet"
            }
        ],
        "sinkhole": {
            "ipv4_address": "pan-sinkhole-default-ip",
            "ipv6_address": "::1"
        },
        "whitelist": [
            {
                "name": "trusteddomain.com",
                "description": "Whitelisted domain"
            }
        ]
    }
}

updated_profile = dns_security_profile.update(new_profile.id, update_data)
print(f"Updated profile with multiple components: {updated_profile.name}")
```

</div>

---

## Full Example: Creating and Managing a DNS Security Profile

<div class="termy">

<!-- termynal -->

```python
from scm.client import Scm
from scm.config.security import DNSSecurityProfile

# Initialize the SCM client
scm = Scm(
    client_id="your_client_id",
    client_secret="your_client_secret",
    tsg_id="your_tsg_id",
)

# Create a DNSSecurityProfile instance
dns_security_profile = DNSSecurityProfile(scm)

# Create a new DNS Security Profile
profile_data = {
    "name": "comprehensive_profile",
    "description": "Comprehensive DNS Security Profile",
    "folder": "Shared",
    "botnet_domains": {
        "dns_security_categories": [
            {
                "name": "grayware",
                "action": "block",
                "log_level": "medium",
                "packet_capture": "single-packet"
            },
            {
                "name": "malware",
                "action": "sinkhole",
                "log_level": "critical",
                "packet_capture": "extended-capture"
            }
        ],
        "lists": [
            {
                "name": "custom_blocklist",
                "action": {"block": {}},
                "packet_capture": "disable"
            },
            {
                "name": "custom_sinkhole_list",
                "action": {"sinkhole": {}},
                "packet_capture": "single-packet"
            }
        ],
        "sinkhole": {
            "ipv4_address": "pan-sinkhole-default-ip",
            "ipv6_address": "::1"
        },
        "whitelist": [
            {
                "name": "example.com",
                "description": "Whitelisted domain"
            },
            {
                "name": "trusteddomain.org",
                "description": "Another trusted domain"
            }
        ]
    }
}

new_profile = dns_security_profile.create(profile_data)
print(f"Created comprehensive profile: {new_profile.name} with ID: {new_profile.id}")

# Retrieve the created profile
retrieved_profile = dns_security_profile.get(new_profile.id)
print(f"Retrieved profile: {retrieved_profile.name}")

# Update the profile
update_data = {
    "description": "Updated comprehensive DNS Security Profile",
    "botnet_domains": {
        "dns_security_categories": [
            {
                "name": "phishing",
                "action": "block",
                "log_level": "high",
                "packet_capture": "extended-capture"
            }
        ]
    }
}

updated_profile = dns_security_profile.update(new_profile.id, update_data)
print(f"Updated profile: {updated_profile.name}")

# List profiles
profiles = dns_security_profile.list(folder='Shared', limit=10)
print("List of profiles:")
for profile in profiles:
    print(f"- {profile.name} (ID: {profile.id})")

# Delete the profile
dns_security_profile.delete(new_profile.id)
print(f"Deleted profile: {new_profile.name}")
```

</div>

---

## Related Models

- [DNSSecurityProfileRequestModel](../../models/security_services/dns_security_profile_models.md#DNSSecurityProfileRequestModel)
- [DNSSecurityProfileResponseModelModel](../../models/security_services/dns_security_profile_models.md#DNSSecurityProfileResponseModel)
