# Mobile Agent Configuration

Configuration objects for managing GlobalProtect mobile agent settings in Strata Cloud Manager.

## Overview

This section covers the Mobile Agent configuration objects provided by the Palo Alto Networks Strata Cloud Manager SDK. These objects correspond to resources related to GlobalProtect mobile VPN services.

## Available Modules

| Module                                                 | Description                                                        |
|--------------------------------------------------------|--------------------------------------------------------------------|
| [Authentication Settings](auth_settings.md)            | Manage GlobalProtect authentication settings by OS                 |
| [Agent Versions](agent_versions.md)                    | List and retrieve available GlobalProtect agent versions           |
| [Application Settings (Agent Profiles)](agent_profiles.md) | Manage GlobalProtect agent profiles (App Settings in the SCM UI) |
| [Forwarding Profiles](forwarding_profiles.md)          | Manage GlobalProtect traffic forwarding profiles                   |
| [Forwarding Profile Destinations](forwarding_profile_destinations.md) | Manage destinations referenced by forwarding profile rules |
| [Forwarding Profile Source Applications](forwarding_profile_source_applications.md) | Manage source applications for forwarding profiles |
| [Forwarding Profile User Locations](forwarding_profile_user_locations.md) | Manage user locations for forwarding profiles |
| [Forwarding Profile Regional and Custom Proxies](forwarding_profile_regional_and_custom_proxies.md) | Manage regional and custom proxies for forwarding profiles |
| [Global Settings](global_settings.md)                  | Manage the GlobalProtect global settings singleton                 |
| [Infrastructure Settings](infrastructure_settings.md)  | Manage GlobalProtect infrastructure (DNS, IP pools, portal, WINS)  |
| [Tunnel Profiles](tunnel_profiles.md)                  | Manage GlobalProtect tunnel settings (split tunneling)             |

## Related Documentation

- [Mobile Agent Models](../../models/mobile_agent/index.md)
- [API Client](../../client.md)
