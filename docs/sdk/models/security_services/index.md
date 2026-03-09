# Security Services Data Models

Pydantic models for validating and serializing security service configuration resources in the Strata Cloud Manager SDK.

## Overview

The Strata Cloud Manager SDK uses Pydantic models for data validation and serialization of security services. These models ensure that the data being sent to and received from the Strata Cloud Manager API adheres to the expected structure and constraints. This section documents the models for security service configuration resources.

## Model Types

For each security service configuration, there are corresponding model types:

- **Create Models**: Used when creating new security resources (`{Object}CreateModel`)
- **Update Models**: Used when updating existing security resources (`{Object}UpdateModel`)
- **Response Models**: Used when parsing security data retrieved from the API (`{Object}ResponseModel`)
- **Base Models**: Common shared attributes for related security models (`{Object}BaseModel`)

## Common Model Patterns

Security service models share common patterns:

- Container validation (exactly one of folder/snippet/device)
- UUID validation for identifiers
- Profile name and description validation
- Reference validation for associated objects
- Security action and severity validation
- Rule ordering and positioning logic

## Usage Examples

### Creating a Security Rule

```python
from scm.client import ScmClient
from scm.models.security import SecurityRuleCreateModel

# Initialize client
client = ScmClient(
   client_id="your_client_id",
   client_secret="your_client_secret",
   tsg_id="your_tsg_id"
)

# Create a new security rule using a model
security_rule = SecurityRuleCreateModel(
   name="allow-web-traffic",
   source=["any"],
   destination=["any"],
   application=["web-browsing"],
   service=["application-default"],
   action="allow",
   folder="Security Policies"
)

# Convert the model to a dictionary for the API call
rule_dict = security_rule.model_dump(exclude_unset=True)
result = client.security_rule.create(rule_dict)
```

### Parsing a Response

```python
from scm.models.security import SecurityRuleResponseModel

response = SecurityRuleResponseModel(**api_response)
print(f"Rule: {response.name}, Action: {response.action}")
```

## Models by Category

### Security Rules

- [Security Rule Models](security_rule_models.md) - Firewall security policy rules

### Anti-Spyware Profile

- [Anti-Spyware Profile Models](anti_spyware_profile_models.md) - Anti-spyware security profiles

### Decryption Profile

- [Decryption Profile Models](decryption_profile_models.md) - SSL/TLS decryption profiles

### Decryption Rule

- [Decryption Rule Models](decryption_rule_models.md) - SSL/TLS decryption rules

### DNS Security Profile

- [DNS Security Profile Models](dns_security_profile_models.md) - DNS security profiles

### File Blocking Profile

- [File Blocking Profile Models](file_blocking_profile_models.md) - File blocking security profiles

### URL Access Profile

- [URL Access Profile Models](url_access_profile_models.md) - URL access filtering profiles

### URL Categories

- [URL Categories Models](url_categories_models.md) - URL category definitions

### Vulnerability Protection Profile

- [Vulnerability Protection Profile Models](vulnerability_protection_profile_models.md) - Vulnerability protection profiles

### WildFire Antivirus Profile

- [WildFire Antivirus Profile Models](wildfire_antivirus_profile_models.md) - WildFire and Antivirus profiles

### App Override Rule

- [App Override Rule Models](app_override_rule_models.md) - Application override rules

### Authentication Rule

- [Authentication Rule Models](authentication_rule_models.md) - Authentication policy rules
