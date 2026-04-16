# Incidents Data Models

Pydantic models for validating and serializing incident-related data in the Strata Cloud Manager SDK.

## Overview

The Incidents models define the data structures for the Unified Incident Framework API. These models handle incident search requests, responses with pagination metadata, and detailed incident information including associated alerts and impacted objects.

## Model Types

- **Request Models**: Used when building search queries with filters and pagination
- **Response Models**: Used when parsing search results and incident details from the API
- **Component Models**: Supporting models for filters, alerts, and impacted objects

## Models by Category

### Search

- [Incidents Models](incidents_models.md) - Search, filter, pagination, incident, and alert models

## Related Documentation

- [Incidents Service](../../incidents/incidents.md)
- [API Client](../../client.md)
