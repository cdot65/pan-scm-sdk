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

- [Address Models](address_models.md)
- [Address Group Models](address_group_models.md)
- [Application Models](application_models.md)
- [Application Filters Models](application_filters_models.md)
- [Application Group Models](application_group_models.md)
- [Dynamic User Group Models](dynamic_user_group_models.md)
- [External Dynamic Lists](external_dynamic_lists_models.md)
- [HIP Object Models](hip_object_models.md)
- [Service Models](service_models.md)
- [Service Group Models](service_group_models.md)
- [Tag Models](tag_models.md)
