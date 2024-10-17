# Introduction

## Overview

The `pan-scm-sdk` is a Python SDK designed to simplify interactions with Palo Alto Networks Strata Cloud Manager (SCM).
It allows developers to programmatically manage configuration objects such as addresses, address groups, and
applications.

## Why Use pan-scm-sdk?

Manually managing configurations in SCM can be time-consuming and prone to errors. The SDK provides a streamlined way to
automate these tasks, ensuring consistency and efficiency.

## Key Features

- **OAuth2 Authentication**: Securely authenticate with the SCM API using OAuth2 client credentials.
- **Resource Management**: Perform CRUD (Create, Read, Update, Delete) operations on configuration objects.
- **Data Validation**: Utilize Pydantic models for robust data validation.
- **Exception Handling**: Comprehensive error handling with custom exceptions.
- **Extensibility**: Easily extend the SDK to support additional resources and endpoints.

## How It Works

1. **Authentication**: Initialize the SDK with your client credentials to establish a secure session.
2. **Manage Resources**: Use the provided classes to interact with various configuration objects.
3. **Integrate into Workflows**: Incorporate the SDK into automation scripts, CI/CD pipelines, or other tools.

## Who Should Use This SDK?

- **Network Engineers** looking to automate configuration tasks.
- **DevOps Professionals** integrating SCM into deployment workflows.
- **Developers** building applications that interact with SCM.

## Getting Help

- **Documentation**: Explore the [Developer Documentation](../sdk/index.md) for detailed guidance.
- **GitHub Repository**: Visit the [pan-scm-sdk GitHub repository](https://github.com/cdot65/pan-scm-sdk) for source
  code and issue tracking.

## Next Steps

Proceed to the [Getting Started Guide](getting-started.md) to set up `pan-scm-sdk` and begin managing your SCM
configurations.
