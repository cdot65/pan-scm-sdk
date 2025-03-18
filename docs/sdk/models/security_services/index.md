# Security Services Data Models

## Table of Contents

1. [Overview](#overview)
2. [Model Types](#model-types)
3. [Common Model Patterns](#common-model-patterns)
4. [Usage Examples](#usage-examples)
5. [Models by Category](#models-by-category)
   1. [Security Rules](#security-rules)
   2. [Anti-Spyware Profile](#anti-spyware-profile)
   3. [Decryption Profile](#decryption-profile)
   4. [DNS Security Profile](#dns-security-profile)
   5. [URL Categories](#url-categories)
   6. [Vulnerability Protection Profile](#vulnerability-protection-profile)
   7. [WildFire Antivirus Profile](#wildfire-antivirus-profile)
6. [Best Practices](#best-practices)
7. [Related Documentation](#related-documentation)

## Overview {#Overview}
<span id="overview"></span>

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

<div class="termy">

<!-- termynal -->
```python
from scm.client import ScmClient
from scm.models.security import SecurityRuleCreateModel, SecurityRuleUpdateModel

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

# Update an existing security rule using a model
update_rule = SecurityRuleUpdateModel(
   id=result.id,
   name="allow-web-traffic-updated",
   description="Updated web traffic rule",
   application=["web-browsing", "ssl"],
   folder="Security Policies"
)

update_dict = update_rule.model_dump(exclude_unset=True)
updated_result = client.security_rule.update(update_dict)
```

</div>

## Models by Category

### Security Rules

- [Security Rule Models](security_rule_models.md) - Firewall security policy rules

### Anti-Spyware Profile

- [Anti-Spyware Profile Models](anti_spyware_profile_models.md) - Anti-spyware security profiles

### Decryption Profile

- [Decryption Profile Models](decryption_profile_models.md) - SSL/TLS decryption profiles

### DNS Security Profile

- [DNS Security Profile Models](dns_security_profile_models.md) - DNS security profiles

### URL Categories

- [URL Categories Models](url_categories_models.md) - URL category definitions

### Vulnerability Protection Profile

- [Vulnerability Protection Profile Models](vulnerability_protection_profile_models.md) - Vulnerability protection profiles

### WildFire Antivirus Profile

- [WildFire Antivirus Profile Models](wildfire_antivirus_profile_models.md) - WildFire and Antivirus profiles

## Best Practices

1. **Model Validation**
   - Always validate security configuration data with models before sending to the API
   - Handle validation errors appropriately for security policy data
   - Use model_dump(exclude_unset=True) to avoid sending default values in security policies

2. **Security Rule Configuration**
   - Ensure source and destination attributes are properly formatted
   - Validate application and service combinations
   - Remember that security rule order is important for policy evaluation
   - Test security rules in a non-production environment first

3. **Security Profile Association**
   - Validate that referenced security profiles exist before associating them with rules
   - Use consistent security profile naming conventions
   - Understand the implications of profile group vs. individual profile attachments

4. **Policy Validation**
   - Test security rules with model validation before deployment
   - Validate security profile settings against expected protection levels
   - Ensure security policies don't conflict with other existing policies

## Related Documentation

- [Security Service Configuration](../../config/security_services/index.md) - Working with security services
- [Security Rule Configuration](../../config/security_services/security_rule.md) - Security rule operations
- [Anti-Spyware Configuration](../../config/security_services/anti_spyware_profile.md) - Anti-spyware profile operations
