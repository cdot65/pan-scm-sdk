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

- [NAT Rules Models](nat_rule_models.md)
