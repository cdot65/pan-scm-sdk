# Data Models

The `pan-scm-sdk` utilizes Pydantic models for data validation and serialization. This ensures that the data being sent
to and received from the Strata Cloud Manager API adheres to the expected structure and constraints.

---

## Overview

For each configuration object, there are corresponding request and response models:

- **Request Models**: Used when creating or updating resources.
- **Response Models**: Used when parsing data retrieved from the API.

---

## Models by Configuration Object

- [Anti Spyware Security Profile Models](anti_spyware_profile_models.md)
- [Decryption Profile Models](decryption_profile_models.md)
- [DNS Security Profile Models](dns_security_profile_models.md)
- [Security Rule Models](security_rule_models.md)
- [URL Categories Models](url_categories_models.md)
- [Vulnerability Protection Profile Models](vulnerability_protection_profile_models.md)
- [Wildfire Antivirus Security Profile Models](wildfire_antivirus_profile_models.md)
