~~# Release Notes

Welcome to the release notes for the `pan-scm-sdk` tool. This document provides a detailed record of changes,
enhancements, and fixes in each version of the tool.

---

## Version 0.2.0

**Release Date:** November 4th

### Updates:

* Add fetch method to various profile and object classes

Implemented a `fetch` method in multiple profile and object classes to retrieve single resources by name. The method
includes validation to ensure exactly one container type is provided and integrates additional filters for detailed
querying.

* Refactor update methods to use data['id'] directly

Updated the `update` methods across various classes to derive the endpoint using `data['id']` instead of passing
`object_id` explicitly. This change optimizes the update process and standardizes the method signatures.

* Simplify update method signatures and improve error handling

Modified the update methods across multiple security profile classes to remove the `object_id` parameter and use the '
id' from the data dictionary instead. Enhanced the DecryptionProfile class with improved error handling and checks for
consistent and clear update operations.

* Refactor update method to use 'id' from data dictionary

The update method now constructs the endpoint URL using the 'id' field from the input data dictionary instead of a
separate object_id parameter. This change simplifies the method signature and makes it more consistent with the rest of
the codebase.

* Add AntiSpywareProfileUpdateModel to anti_spyware_profiles

Add a new model, AntiSpywareProfileUpdateModel, for handling updates to anti-spyware profiles. This includes fields for
profile ID, folder, snippet, device, rules, and threat exceptions. This change facilitates more comprehensive API
requests related to anti-spyware profiles.

* Refine error type extraction logic in client.py

Updated the error type extraction to handle cases where 'details' can be either a dict or a list. This ensures proper
concatenation of error messages when 'details' is a list and improves overall error handling robustness.

* Refactor address group response handling

Revised the handling of API responses for address group lookups to cater to both single-object and list formats. Added
specific error handling for cases where no or multiple address groups are found, improving robustness and error
transparency. Included additional exceptions for more detailed error reporting.

* Refactor address group response handling

Revised the handling of API responses for address group lookups to cater to both single-object and list formats. Added
specific error handling for cases where no or multiple address groups are found, improving robustness and error
transparency. Included additional exceptions for more detailed error reporting.

* Refactor Address models to separate base, create, update, and response logic.

Refactored `AddressRequestModel` into distinct `AddressBaseModel`, `AddressCreateModel`, `AddressUpdateModel`, and
`AddressResponseModel` for clarity and maintainability. Added custom validators and consolidated common fields into
`AddressBaseModel` to ensure consistent validation rules across create, update, and response operations.

* Refactor address models in address.py

Changed import statements and updated methods to use AddressCreateModel and AddressUpdateModel instead of
AddressRequestModel. This ensures a clearer distinction between create and update operations in handling address data.

* Rename AddressRequestModel to AddressCreateModel

This update refactors the documentation to rename `AddressRequestModel` to `AddressCreateModel` for clarity and
consistency. All relevant instances of `AddressRequestModel` have been updated accordingly throughout the files.

* Refactor error handling and add detailed docstrings

Enhanced error handling across Address methods with specific exceptions. Added detailed docstrings for each method to
clarify the API behavior and possible exceptions raised. This improves code robustness and maintainability.

* Add detailed error handling and new exception classes

Introduced `ReferenceDetail` and `ErrorResponse` dataclasses for standardized handling of errors. Enhanced `APIError`
and its subclasses with additional attributes and methods like `from_error_response`. Added `ErrorHandler` for mapping
error responses to appropriate exception classes and included new exceptions for specific cases.

* Validate presence of exactly one address type

Add docstrings to clarify that the validators ensure exactly one of the fields 'ip_netmask', 'ip_range', 'ip_wildcard',
or 'fqdn' is provided. Refine the validation logic to explicitly handle cases where no field or more than one field is
provided.

* Add new Address factories for various address models

Introduce new factories: AddressCreateIpNetmaskFactory, AddressCreateFqdnFactory, AddressCreateIpRangeFactory, and
AddressCreateIpWildcardFactory to support various AddressCreateModel instances. Update imports and adjust existing
factory classes to align with the new AddressCreateModel instead of AddressRequestModel.

* Enhance address handling and testing in SCM

Extend address functions to cover various types like `ip-netmask`, `fqdn`, `ip-range`, and `ip-wildcard`. Added
comprehensive test cases for CRUD operations, including validations and error handling, and enhanced mock responses to
ensure realistic API simulations.

* Add detailed exception handling for API-specific errors

Enhanced the error handling in `scm/client.py` to include specific exceptions like `ObjectNotPresentError`,
`FolderNotFoundError`, `MalformedRequestError`, and `EmptyFieldError`. Updated the `_handle_api_error` method to first
address API-specific error codes before falling back to status code-based handling.

* Move test_addresses.py to scm/config directory

This change reorganizes the test file structure for better modularity. The test_addresses.py file is now located in the
scm/config directory to match the updated project layout.

* Refactor test_auth.py and add new AuthRequestModel tests

Moved `test_auth.py` to the `tests/scm` directory for better organization. Added new tests for `AuthRequestModel` to
validate various scenarios including scope handling, token URL defaults, and missing `tsg_id` exceptions.

* Remove test_models.py file

Removed the `test_models.py` file since its tests are no longer relevant or required. This change addresses the need to
clean up outdated or redundant test cases, ensuring the codebase remains maintainable and focused on current
requirements.

* Refactor and expand error handling tests in SCM

Renamed `test_client.py` to `scm/test_client.py` for better organization. Added new test cases to handle a wider variety
of API error scenarios, including Object Not Present, Folder Not Found, Object Already Exists, Malformed Request, and
Empty Field validation errors. Commented out some assertions for later review.

* Remove redundant else clause in error handling code

The unnecessary `else` clause setting `error_type` to an empty string has been removed, as it doesn't affect the
existing logic. This simplifies the code and makes it easier to maintain.

* Relocate test_address_groups.py to new directory

Moved test_address_groups.py to scm/config to better organize tests by their context and group related files together.
This enhances maintainability and readability of the test suite.

* Restructure test modules for better organization.

Renamed test files to new directory structure under `tests/scm/config/objects` for improved organization and
maintainability. Updated imports and class structures to reflect these changes, ensuring that the unit tests remain
consistent and functional.

* Refactor AddressGroup models for CRUD operations

Reorganized AddressGroup models to separate base, create, and update operations. Modified tests and factory imports to
use new models, ensuring validation rules are maintained and improving clarity in the model definitions.

* Refactor model imports and update methods in application.py

Updated import statements and refactored methods to use `ApplicationCreateModel` and `ApplicationUpdateModel` instead of
`ApplicationRequestModel` for consistency and clarity. Removed obsolete filtering by names in the list method.

* Rename test files for address and address group objects

This change renames `test_addresses.py` to `test_address.py` and `test_address_groups.py` to `test_address_group.py` to
ensure consistency with the naming convention. This improves clarity and aligns the test file names with the object
names they are testing.

* Refactor test structure and improve validation

Renamed and reorganized test files for better structure and clarity. Introduced a base class for common test setup and
segregated tests into specific categories for API operations, validation, and filtering. Enhanced validation checks and
response handling to ensure robust error handling.

* Update factory model and rename test file

Changed the model in `ApplicationFactory` from `ApplicationRequestModel` to `ApplicationCreateModel` for consistency
with current codebase. Also, renamed `tests/scm/config/objects/test_application_groups.py` to
`tests/test_application_groups.py` for better file organization and accessibility.

* Refactor application models for better structure

Simplify model hierarchy by introducing a common ApplicationBaseModel for shared fields and validation logic. Split the
previous ApplicationRequestModel into distinct models for create, update, and response actions, improving code
readability and maintainability.

* Rename and add application models

Replaced ApplicationRequestModel with ApplicationCreateModel in __init__.py for better clarity and usability. Added
ApplicationUpdateModel to support update operations in the application module.

* Refactor Application Group models to enhance modularity

Refactored the Application Group models by introducing an ApplicationGroupBaseModel to consolidate shared fields and
validation logic. Added specific models for create, update, and response operations to improve clarity and
maintainability. This change also updates import statements and removes redundant comments.

* Update application group models to use Create and Update types

Replaced `ApplicationGroupRequestModel` with `ApplicationGroupCreateModel` for create and get methods and introduced
`ApplicationGroupUpdateModel` for update methods in `application_group.py`. This ensures more specific model usage for
different operations, enhancing code clarity and reliability.

* Rename test file, add fetch tests, update model usage

Renamed the test file to a more specific path. Added new tests for fetching application groups, validating parameter
handling, and response transformation. Updated references to the model from ApplicationGroupRequestModel to
ApplicationGroupCreateModel.

* Remove unused imports

In `test_application.py`, the NotFoundError and APIError imports were removed as they are not used. In
`test_application_group.py`, a clarification comment was added at the top of the file.

* Refactor service request model in service.py

Replaced ServiceRequestModel with ServiceCreateModel for creating and updating services to better align with API
specifications. This change ensures consistent request payload structures and improves code maintainability.

* Refactor service models for CRUD operations

Reorganized service models into base, create, update, and response models to streamline validation and enhance code
readability. Included detailed model docstrings and validation logic to improve maintainability and clarity.

* Refactor and enhance service tests; rename and reorganize files

Renamed and restructured test files for better organization. Introduced class-based test structures and added detailed
docstrings to each test method. Improved parameter validation and response handling in service-related tests.

* Add tests for BaseObject class and implement validation

Created comprehensive unit tests for the BaseObject class in the scm module, covering initialization, CRUD operations,
and error handling. Implemented endpoint definition and API client type validation in the BaseObject constructor.

* Refactor and extend anti-spyware profile tests.

Renamed test file for better organization under SCM hierarchy. Added comprehensive test cases for fetching anti-spyware
profiles with various parameters and conditions. Included UUID and ID format validation in the response and update
models.

* Refactor decryption profile models and tests

Streamline decryption profile models by removing unnecessary classes and improving field descriptions. Consolidate and
refactor tests for better organization and readability. This enhances code maintainability and aligns with PEP8
standards.

* Rename DNS Security Profile model classes and references

Updated model class names in the DNS Security Profile documentation to maintain consistent naming conventions. This
includes changing class names such as `DNSSecurityCategoryEntry` to `DNSSecurityCategoryEntryModel` and updating
corresponding import statements and method signatures.

* Refactor DNS security profile models for clarity and consistency

Consolidate various DNS security profile models, renaming classes for clarity and introducing base models for reusable
components. Update `create` and `update` methods to use new models, ensuring validation and type safety.

* Refactor and validate DNS security profiles tests

Renamed the DNS security profile test file for better organization. Updated model imports and test functions, ensuring
accurate validation checks and streamlined mock responses. Added multiple tests for fetch method validations and updated
model fields.

* Update DNSSecurityProfile*Model references to new names

Refactor the code to align with the updated model class names for better consistency. Changed all
`DNSSecurityProfileRequestModel` references to `DNSSecurityProfileCreateModel` and similarly updated other model names
accordingly. These changes aim to enhance code readability and maintainability.

* Add noqa comments to mock_scm.get return value lines

This update adds `# noqa` comments to all instances where `self.mock_scm.get.return_value` is being set in the
`test_dns_security_profile.py` file. This change is made to suppress any style or linting warnings related to these
lines. These modifications ensure that the test code adheres to the specified coding standards.

* Refactor test file structure and update unit tests

Renamed test file and improved unit test logic for updating and fetching security rules. Adjusted ID handling within
test update methods and added new tests for the fetch method of SecurityRule with varied scenarios.

* Refactor test to comply with static code analysis rules

Applied `# noqa` comments to silence specific static code analysis warnings without altering the logic. This helps in
maintaining code quality and readability while adhering to linting rules. Also, removed an unused import for better
readability and reduced clutter.

* Rename request model and clean up docstrings

Replaced VulnerabilityProtectionProfileRequestModel with VulnerabilityProtectionProfileCreateModel. Additionally,
removed unnecessary verbosity from docstrings and made minor formatting improvements for better clarity and consistency.

* Move vulnerability protection profile tests to new location

The vulnerability protection profile tests have been relocated for better organization and modularity. The test fixtures
and setup methods were consolidated in a base class to ensure DRY (Don't Repeat Yourself) principles.

* Update WildfireAntivirusProfile models and API logic

Switched from `WildfireAntivirusProfileRequestModel` to more specific create and update models for profile handling.
This refactoring improves clarity and validation, ensuring better control over the profile creation and update
processes.

* Refactor Wildfire Antivirus Profile tests structure

Reorganized the test file structure for better modularity. Introduced base classes and fixtures to reduce redundancy and
improve maintainability. Enhanced tests with detailed workflows and added new cases for pagination and error handling.

* Fix uninitialized message attribute and add exception tests

Add the 'message' attribute initialization in APIError class constructor to avoid potential uninitialized attribute
errors. Introduce comprehensive tests for ErrorResponse, APIError, and ErrorHandler classes to ensure robustness and
accurate error handling.

* Add UUID validation test for ResponseModel

This update introduces a new test to validate UUID format in the `ResponseModel` within the Wildfire Antivirus Profiles
module. It includes checks for both valid and invalid UUID formats to ensure robust input validation.

* Add initial junit.xml file for CI/CD integration

This update introduces the junit.xml file necessary for continuous integration and deployment processes. Having this XML
file will facilitate better test reporting and automated deployment workflows.

* Revise documentation for WildFire and Anti-Spyware profiles

Simplified and enhanced the WildFire and Anti-Spyware profile setup guides. Added examples for creating, updating,
deleting, and listing profiles. Clarified method descriptions and updated formatting for better readability.

* Refactor docs

This update restructures the application group models to improve clarity and validation, ensuring better management of
application groups. The address and security models were also updated to align with the new standards, focusing on
validation and usage examples.

---

## Version 0.1.17

**Release Date:** October 26, 2024

### Added `move` method for Security Policy

- **New `move` method**: Add ability to move security rules within the rule base.

---

## Version 0.1.16

**Release Date:** October 23, 2024

### Correcting `create` method for Security Policy

- **Updated `create` method**: Missing keys within a dictionary will now be properly set with default values.

---

## Version 0.1.15

**Release Date:** October 23, 2024

### Correcting pattern for Security Policy name

- **Updated pattern**: Added support for periods (.) within the name of security policies.

---

## Version 0.1.14

**Release Date:** October 21, 2024

### Adding Security Rules

- **New Configuration**: Added support for Security Rules.

---

## Version 0.1.13

**Release Date:** October 19, 2024

### Adding Decryption Profiles

- **New Configuration**: Added support for Decryption Profiles.

---

## Version 0.1.12

**Release Date:** October 18, 2024

### Adding DNS Security Profiles

- **New Configuration**: Added support for DNS Security Profiles.

---

## Version 0.1.11

**Release Date:** October 18, 2024

### Adding Vulnerability Protection Profiles

- **New Configuration**: Added support for Vulnerability Protection Profiles.

---

## Version 0.1.10

**Release Date:** October 18, 2024

### Bug fix

- **Update Methods**: Added support for empty responses from the API, common for PUT updates.

---

## Version 0.1.9

**Release Date:** October 17, 2024

### Wildfire Antivirus Security Profiles

- **Wildfire Antivirus**: Add support for managing Wildfire Anti-Virus Security Profiles.

---

## Version 0.1.8

**Release Date:** October 16, 2024

### Anti Spyware Profiles

- **Pytests**: Add the pytests to support Anti Spyware Profiles.

---

## Version 0.1.7

**Release Date:** October 16, 2024

### Anti Spyware Profiles

- **Anti Spyware Profiles**: Add the ability to support Anti Spyware Profiles.

---

## Version 0.1.6

**Release Date:** October 15, 2024

### Logging

- **Logging**: Changed logging to INFO by default.

---

## Version 0.1.5

**Release Date:** October 15, 2024

### Application Groups

- **New Object**: Add the ability to support Address Groups.
- **Docs Update**: Update the mkdocs site.

---

## Version 0.1.4

**Release Date:** October 13, 2024

### Services

- **New Object**: Add the ability to support Services.
- **Docs Update**: Update the mkdocs site.

---

## Version 0.1.3

**Release Date:** October 12, 2024

### Application

- **New Object**: Add the ability to support Applications.
- **Docs Update**: Revamp the readme and mkdocs site.

---

## Version 0.1.2

**Release Date:** October 10, 2024

### Refactoring Names

- **Refactoring Names**: Refactor the project to have simpler naming convention.

---

## Version 0.1.1

**Release Date:** October 10, 2024

### Object-Oriented

- **Refactor**: Refactor the project to work in an object-oriented manner.

---

## Version 0.1.0

**Release Date:** October 9, 2024

### Introduction

- **Initial Release**: Developer version of `pan-scm-sdk`.

---

For more detailed information on each release, visit
the [GitHub repository](https://github.com/cdot65/pan-scm-sdk/releases) or check
the [commit history](https://github.com/cdot65/pan-scm-sdk/commits/main).
