# Setup Configuration Objects

## Overview

The Setup section contains configuration objects related to organization and setup of resources in Palo Alto Networks'
Strata Cloud Manager. These objects form the foundation for organizing and managing your environment.

## Available Setup Configuration Objects

| Configuration Object        | Description                                                                 |
|-----------------------------|-----------------------------------------------------------------------------|
| [Device Service](device.md) | List, filter, and manage device resources                                   |
| [Folder](folder.md)         | Manages folder objects for organizing resources in a hierarchical structure |
| [Snippet](snippet.md)       | Manages reusable configuration snippets for consistent deployment           |
| [Variable](variable.md)     | Create and manage variable resources with flexible typing and containers    |

## Folder Organization

Folders are used to organize resources in a hierarchical structure in the Strata Cloud Manager. They form the foundation
of resource organization and provide the following benefits:

- Logical organization of resources by function, team, or purpose
- Hierarchical navigation through nested folder structures
- Inheritance of policies and configurations from parent folders
- Simplified management of resource permissions

See the [Folder](folder.md) documentation for detailed information on working with folder objects.

## Snippet Management

Snippets are reusable configuration elements that help maintain consistency across your environment. They provide the
following advantages:

- Standardized configurations that can be applied consistently
- Reduced duplication of common configuration patterns
- Simplified maintenance through centralized configuration management
- Ability to associate snippets with folders for organization

See the [Snippet](snippet.md) documentation for detailed information on working with snippet objects.

## Variable Management

Variables allow for dynamic configurations and parameterization of resources. They provide the following capabilities:

- Typed variables for different usage contexts (IP addresses, percentages, etc.)
- Container scoping to folders, snippets, or devices
- Client-side filtering by various attributes (labels, parent, type, snippets, etc.)
- Support for labeling and organization
- Advanced filtering with intersection matching for collections

Variables support 18 different types including:
- `percent`: Percentage values
- `count`: Numeric count values
- `ip-netmask`: IP address with netmask
- `ip-range`: Range of IP addresses
- `ip-wildcard`: IP address with wildcard
- `fqdn`: Fully qualified domain names
- And many more specialized types

See the [Variable](variable.md) documentation for detailed information on working with variable resources.
