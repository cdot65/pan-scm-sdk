# Release Notes

This page contains the release history of the Strata Cloud Manager SDK, with the most recent releases at the top.

## Version 0.3.37

**Released:** May 17, 2025

### Improved & Enforced
- **Docstring Linting:**
  - Enforced Ruff for all docstrings across the SDK, adopting Google-style docstrings as the project standard.
  - Suppressed mutually exclusive rule warnings (D203/D211, D212/D213) for a clean, warning-free linting experience.
  - All docstrings now linted and auto-fixed by Ruff; documentation consistency guaranteed for all modules and releases.

### Improved
- **OAuth Token Refresh:**
  - Improved handling of OAuth token refreshing in `scm/auth.py` for more robust and reliable authentication flows.

## Version 0.3.36

**Released:** May 16, 2025

### Fixed & Improved
- **Log Forwarding Profile:**
  - Hotfix: Fetch logic now robustly handles all valid and invalid API response shapes, raising precise exceptions for missing, malformed, or empty data.
  - Full error handling for all edge cases, including missing or non-dict API responses, and explicit validation of container parameters.
  - Achieved 100% test coverage for all Log Forwarding Profile logic and error branches.
  - All tests updated to match real API response structure and new error handling.

## Version 0.3.35

**Released:** May 16, 2025

### Fixed
- **Log Forwarding Profile:**
  - Hotfix: The SDK now always returns a `LogForwardingProfileResponseModel` from API responses, even if the `id` field is missing or `None`. This prevents unnecessary errors for valid profiles where `id` can be `None`.
  - Updated tests to reflect new behavior and ensure robust error handling for all valid API responses.

## Version 0.3.34

**Released:** May 16, 2025

### Fixed
- **Log Forwarding Profile:**
  - Added support for the `dns-security` log_type in LogForwardingProfile models and API validation.
  - Resolves user validation errors when listing or handling profiles containing `dns-security` entries.
  - Motivation: The SDK previously rejected LogForwardingProfile objects with `dns-security` match_list entries, causing failures for users with such log types configured in their environments. This release ensures full compatibility with all supported log types from the API.

## Version 0.3.33

**Released:** May 11, 2025

### Fixed
- **Variable Service:**
  - Fixed bug in the `fetch()` method of the `Variable` class by requiring a `folder` parameter to properly identify variables
  - Updated the method signature to require both `name` and `folder` parameters for more precise variable lookup
  - Added proper validation for empty name or folder parameters
  - Updated documentation and examples to reflect the new parameter requirements
  - Enhanced test coverage for the `fetch()` method with various test cases
  - Achieved 100% test coverage for all variable-related functionality

## Version 0.3.32

**Released:** May 9, 2025

### Improved
- **Bearer Token Authentication:**
  - Enhanced bearer token authentication with comprehensive testing
  - Improved error handling for commit operations when using bearer token authentication
  - Added clear error messaging when admin parameter is required for commit operations with bearer token authentication
  - Consolidated test coverage for bearer token functionality
  - Achieved 100% test coverage for all client authentication methods

### Fixed
- **Testing Infrastructure:**
  - Fixed inconsistencies in error message validation in tests
  - Improved test reliability for bearer token authentication
  - Enhanced test organization for better maintainability

## Version 0.3.31

**Released:** May 9, 2025

### Added
- **Label Support:**
  - Implemented `Label` service for creating, retrieving, updating, and deleting label resources in the SCM API
  - Added Pydantic models for label validation and serialization
  - Created comprehensive documentation for Label service with examples
  - Integrated Label service with the unified client interface
  - Added new Label documentation pages to mkdocs

### Improved
- **Documentation:**
  - Added Label entry to all index pages and navigation
  - Updated README.md to include Label in the available client services table
  - Enhanced documentation structure for consistent navigation

## Version 0.3.30

**Released:** May 4, 2025

### Improved
- **Documentation:**
  - Updated documentation for setup module objects (Device, Folder, Snippet, Variable) to use consistent formatting
  - Added unified client interface examples to all setup module documentation
  - Standardized Basic Configuration sections across all setup module objects
  - Fixed initialization examples to use proper credentials (client_id, client_secret, tsg_id)
  - Enhanced documentation readability with consistent structure and format

## Version 0.3.29

**Released:** May 4, 2025

### Fixed
- **HTTP Server Profiles:**
  - Fixed inconsistent API response format in the `fetch()` method of HTTP Server Profiles
  - Added support for both direct object response and list-style data array format
  - Enhanced error handling for empty responses
  - Added comprehensive test coverage for both response formats
  - Resolves issue #182

## Version 0.3.28

**Released:** May 4, 2025

### Added
- **Variable Service:**
  - Implemented `Variable` service for creating, retrieving, updating, and deleting variable resources in the SCM API.
  - Added client-side filtering by labels, parent, type, snippets, model, serial_number, and device_only.
  - Created comprehensive Pydantic models for variable validation and serialization with 18 supported variable types.
  - Implemented container validation to ensure exactly one of folder, snippet, or device is specified.
  - Added advanced filtering with intersection matching for labels and snippets.
  - Developed robust factories for variable models with proper attribute handling.
  - Achieved 100% test coverage for all variable-related functionality.
- **Documentation:**
  - Added SDK reference pages for Variable service and Variable models.
  - Updated all relevant index and navigation files to include Variable documentation.

### Improved
- Enhanced model handling for attributes not explicitly defined in OpenAPI specs but present in API responses.
- Refined client-side filtering mechanisms for better performance across large datasets.

## Version 0.3.27

**Released:** April 27, 2025

### Added
- **Device Service:**
  - Implemented `Device` service for listing, filtering, and managing device resources in the SCM API.
  - Added server-side and client-side filtering, pagination, and device-specific operations.
  - Created full Pydantic models for device resources and licenses (`DeviceResponseModel`, `DeviceLicenseModel`, etc).
  - Developed factories for device models for robust test data generation.
  - Achieved 100% test coverage for all device-related logic, including edge cases and error handling.
- **Documentation:**
  - Added SDK reference pages for Device service and Device models.
  - Updated all relevant index and navigation files to include Device documentation.

### Fixed
- Improved test reliability by removing unnecessary skips and clarifying skip reasons.
- Fixed import errors and naming consistency across device models, factories, and tests.
- Fixed issue with HIP object validation of response models.

### Changed
- Refactored device model and service structure for clarity and maintainability.
- Enhanced test factories and model validation for device-related resources.

## Version 0.3.26

**Released:** April 16, 2025

### Added

- **Snippet Service**:
  - Implemented comprehensive `Snippet` service class for managing snippet resources
  - Added Pydantic models for snippet validation and serialization
  - Created full CRUD operations for snippet resources
  - Developed folder association functionality (API preview)
  - Implemented robust error handling and data validation
  - Added support for filtering and pagination in list operations
  - Achieved 100% test coverage for all snippet functionality

## Version 0.3.25

**Released:** April 14, 2025

### Improved

- **Test Architecture**:
  - Comprehensive reorganization of test factories into dedicated directories
  - Implemented specialized factories for numerous components:
    - Security profiles (Anti-spyware, DNS Security, Decryption, WildFire Antivirus)
    - Network components (Remote Networks, Internal DNS Servers, BGP Routing)
    - Object configurations (Tags, Services, Service Groups, Schedules)
    - Security rules and policies
  - Enhanced test modularity and maintainability through standardized factory patterns
  - Improved code organization with consistent import structure
  - Removed legacy and redundant factory classes

### Fixed

- **Code Quality**:
  - Standardized import formatting across test modules
  - Improved code organization with dedicated test utility modules
  - Enhanced mypy configuration for better type checking of test modules

## Version 0.3.24

**Released:** April 11, 2025

### Added

- **Enhanced Model Flexibility**:
  - **Syslog Server Profiles**: Refactored models to support greater configuration flexibility
  - **Log Forwarding Profiles**: Redesigned for improved adaptability to various logging scenarios
  - **Authentication Fields**: Added support for additional authentication options in security models
  - **PayloadFormat Model**: Enhanced to support more diverse formatting requirements

### Improved

- **Test Architecture**:
  - Implemented factory pattern for security models (Syslog Server Profiles, URL Categories)
  - Enhanced test coverage and maintainability through standardized test factories
  - Added comprehensive tests for URL Categories Update and Response models

### Documentation

- **SDK Documentation**: Updated model documentation with enhanced details and usage examples
- **Code Examples**: Added examples demonstrating the new model capabilities

## Version 0.3.23

**Released:** March 29, 2025

### Fixed

- **Security Rule Move Operation**: Fixed UUID serialization issue in the `.move()` method of `SecurityRule` class
  - Previously, when a UUID object was passed as `destination_rule` parameter, JSON serialization would fail
  - Now properly converts UUID objects to strings before sending to the API
- **Example Scripts**: Added example script for testing security rule move operations
  - Demonstrates proper handling of UUID serialization
  - Includes improved error handling for edge cases

## Version 0.3.22

**Released:** March 18, 2025

### Added

- **Mobile Agent Features**:
  - **Agent Version**: Support for managing GlobalProtect agent versions
  - **Authentication Setting**: Support for configuring GlobalProtect authentication settings

### Fixed

- **API Endpoint Path**: Fixed 404 error in agent_versions API endpoint path by adding missing '/config' prefix
- **Documentation**: Fixed inconsistencies between code and documentation regarding client service property names
  - Corrected references from `client.auth_setting` to `client.auth_setting`
  - Corrected references from `client.agent_version` to `client.agent_version`
  - Updated code examples to use correct API client attribute names

## Version 0.3.21

**Released:** March 16, 2025

### Added

- **Prisma Access Features**:
  - **Bandwidth Allocation**: Support for managing bandwidth allocation across service provider networks (SPNs)
  - **BGP Routing**: Support for configuring and managing BGP routing
  - **Internal DNS Server**: Support for configuring internal DNS servers
  - **Network Location**: Support for managing network locations

## Version 0.3.20

**Released:** March 13, 2025

### Fixed

- **Security Zone**: Added temporary workaround for inconsistent API response format in the `fetch()` method
  - Now supports both direct object response format and list-style data array format
  - Ensures backward compatibility when API format is corrected
  - Comprehensive test coverage for both response formats

## Version 0.3.19

**Released:** March 12, 2025

### Added

- **NAT Rules**: Support for managing tags not named "Automation" and "Decryption". Oof.

## Version 0.3.18

**Released:** March 8, 2025

### Added

- **Service Connections**: Support for managing Service Connection objects
  - Create, retrieve, update, and delete service connections
  - Filter service connections by name and other attributes
  - Integration with the unified client interface
  - Automatic validation of input parameters
  - Full pagination support with configurable limits

### Improved

- **Code Quality**: Enhanced validation for API parameters
- **Documentation**: Added comprehensive Service Connection documentation and usage examples

## Version 0.3.17

**Released:** March 7, 2025

### Added

- **IKE Crypto Profile**: Support for managing IKE Crypto Profiles
- **IKE Gateway**: Support for managing IKE Gateways
- **IPsec Crypto Profile**: Support for managing IPsec Crypto Profiles

## Version 0.3.16

**Released:** March 6, 2025

### Added

- **Security Zone**: Support for managing Security Zones
- **Examples**: Added examples for each of the objects and network service files

### Fixed

- **Custom Token URL Support**: Fixed issue where `token_url` parameter defined in `AuthRequestModel` wasn't exposed through the `Scm` and `ScmClient` constructors. Users can now specify custom OAuth token endpoints when initializing the client.
- **Documentation Updates**: Added comprehensive documentation for the `token_url` parameter

## Version 0.3.15

**Released:** March 2, 2025

### Added

- **HTTP Server Profile**: Support for managing HTTP Server Profiles
- **Log Forwarding Profile**: Support for managing Log Forwarding Profiles
- **SYSLOG Server Profile**: Support for managing SYSLOG Server Profiles

## Version 0.3.14

**Released:** February 28, 2025

### Added

- **Unified Client Interface**: New attribute-based access pattern for services (e.g., `client.address.create()` instead of creating separate service instances)
- **ScmClient Class**: Added as an alias for the Scm class with identical functionality but more descriptive name
- **Comprehensive Tests**: Added test suite for the unified client functionality
- **Enhanced Documentation**: Updated documentation to showcase both traditional and unified client patterns

### Improved

- **Developer Experience**: Streamlined API usage with fewer imports and less code
- **Token Refresh Handling**: Unified token refresh across all service operations

## Version 0.3.13

**Released:** February 22, 2025

### Added

- **HTTP Server Profiles**: Support for managing HTTP server profiles

## Version 0.3.12

**Released:** February 18, 2025

### Added

- **Dynamic User Groups**: Support for managing dynamic user groups
- **HIP Profiles**: Support for managing HIP profiles

## Version 0.3.11

**Released:** February 15, 2025

### Added

- **Commit Enhancement**: Support for passing the string value of "all" to a commit to specify all admin users

## Version 0.3.10

**Released:** February 12, 2025

### Added

- **Security Rule Enhancement**: Support for new security rule types of SWG by allowing the `device` field to be either string or dictionary

## Version 0.3.9

**Released:** February 8, 2025

### Added

- **NAT Rules**: Support for managing NAT rules

## Version 0.3.8

**Released:** February 5, 2025

### Added

- **Remote Networks**: Support for managing remote networks
- **SASE API Integration**: First time leveraging SASE APIs until Remote Network endpoints for SCM API are working properly

## Version 0.3.7

**Released:** February 2, 2025

### Added

- **HIP Objects**: Support for managing HIP objects

## Version 0.3.6

**Released:** January 28, 2025

### Added

- **Pagination**: Auto-pagination when using the `list()` method
- **Request Control**: Support for controlling the maximum amount of objects returned in a request (default: 2500, max: 5000)

## Version 0.3.5

**Released:** January 25, 2025

### Added

- **Advanced Filtering**: Support for performing advanced filtering capabilities

## Version 0.3.4

**Released:** January 22, 2025

### Added

- **External Dynamic Lists**: Support for managing External Dynamic Lists
- **Auto Tag Actions**: Support for Auto Tag Actions (not yet supported by API)

## Version 0.3.3

**Released:** January 18, 2025

### Added

- **URL Categories**: Support for managing URL Categories

## Version 0.3.2

**Released:** January 15, 2025

### Added

- **Commit Operations**: Support for performing commits
- **Job Status**: Support for pulling in job status

## Version 0.3.1

**Released:** January 12, 2025

### Added

- **Service Group Objects**: Support for managing Service Group objects

## Version 0.3.0

**Released:** January 8, 2025

### Added

- **Tag Objects**: Support for managing tag objects
- **Model Integration**: `fetch()` returns a Pydantic modeled object now
- **Model Update**: `update()` supports passing of Pydantic modeled objects

### Changed

- **Exceptions**: Refactored exception handling
- **Logging**: Refactored logging system

### Fixed

- **OAuth Client**: Fixed issue with refresh_token handling

## Version 0.2.2

**Released:** January 5, 2025

### Changed

- **Dependencies**: Dropped dependency version on crypto package

## Version 0.2.1

**Released:** January 2, 2025

### Added

- **Client-side Filtering**: Added filtering to address list method

### Improved

- **Error Handling**: Enhanced error handling across Address and Application modules
- **Testing**: Improved address and address group tests with better validation

### Changed

- **Object Management**: Refactored address object management

### Fixed

- **Exception Handling**: Introduced `BadResponseError` for invalid API responses

## Version 0.2.0

**Released:** December 28, 2024

### Added

- **Fetch Method**: Added `fetch` method to various profile and object classes
- **Model Updates**: Introduced `AntiSpywareProfileUpdateModel`

### Changed

- **Update Methods**: Refactored update methods to use `data['id']` directly
- **Error Handling**: Improved error type extraction logic in client
- **Model Architecture**: Refactored Address models for separate base, create, update, and response logic

## Version 0.1.17

**Released:** December 25, 2024

### Added

- **Rule Movement**: Added `move` method to enable moving security rules within the rule base

## Version 0.1.16

**Released:** December 22, 2024

### Fixed

- **Create Method**: Updated `create` method to ensure missing dictionary keys are set with default values

## Version 0.1.15

**Released:** December 18, 2024

### Changed

- **Pattern Support**: Updated pattern to support periods (.) in security policy names

## Version 0.1.14

**Released:** December 15, 2024

### Added

- **Security Rules**: Support for Security Rules configuration

## Version 0.1.13

**Released:** December 12, 2024

### Added

- **Decryption Profiles**: Support for Decryption Profiles

## Version 0.1.12

**Released:** December 8, 2024

### Added

- **DNS Security Profiles**: Support for DNS Security Profiles

## Version 0.1.11

**Released:** December 5, 2024

### Added

- **Vulnerability Protection Profiles**: Support for Vulnerability Protection Profiles

## Version 0.1.10

**Released:** December 2, 2024

### Fixed

- **API Response Handling**: Support for empty API responses for PUT updates

## Version 0.1.9

**Released:** November 28, 2024

### Added

- **Wildfire Antivirus**: Support for managing Wildfire Anti-Virus Security Profiles

## Version 0.1.8

**Released:** November 25, 2024

### Added

- **Testing**: Added tests to support Anti Spyware Profiles

## Version 0.1.7

**Released:** November 22, 2024

### Added

- **Anti Spyware Profiles**: Support for Anti Spyware Profiles

## Version 0.1.6

**Released:** November 18, 2024

### Changed

- **Logging**: Changed default logging level to INFO

## Version 0.1.5

**Released:** November 15, 2024

### Added

- **Address Groups**: Support for Address Groups

### Improved

- **Documentation**: Updated the mkdocs site

## Version 0.1.4

**Released:** November 12, 2024

### Added

- **Services**: Support for Services

### Improved

- **Documentation**: Updated the mkdocs site

## Version 0.1.3

**Released:** November 8, 2024

### Added

- **Applications**: Support for Applications

### Improved

- **Documentation**: Revamped README and mkdocs site

## Version 0.1.2

**Released:** November 5, 2024

### Changed

- **Refactoring**: Simplified naming conventions across the project

## Version 0.1.1

**Released:** November 2, 2024

### Changed

- **Architecture**: Transitioned the project to an object-oriented structure

## Version 0.1.0

**Released:** October 30, 2024

### Added

- **Initial Release**: Developer version of `pan-scm-sdk`

---

For more detailed information on each release, visit the [GitHub repository](https://github.com/cdot65/pan-scm-sdk/releases) or check the [commit history](https://github.com/cdot65/pan-scm-sdk/commits/main).
