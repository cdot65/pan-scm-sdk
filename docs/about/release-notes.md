~~# Release Notes

Welcome to the release notes for the `pan-scm-sdk` tool. This document provides a detailed record of changes,
enhancements, and fixes in each version of the tool.

---

## Version 0.2.2

**Release Date:** November 21st

### Updates:

* Drop dependency version on crypto package

---

## Version 0.2.1

**Release Date:** November 12th

### Updates:

* Add client-side filtering to address list method

Introduced a new method `_apply_filters` to perform client-side filtering based on types, values, and tags. Updated the
`list` method to use this filtering and added a high limit for comprehensive results by default.

* Refactor address object management and add error handling

Refactor the address object methods to improve readability and maintainability. Simplify error handling by consolidating
custom error responses, and ensure proper validation for filters. Additionally, enhance comments to provide clearer
guidance on the methods' implementations.

* Add BadResponseError to exceptions module

Introduced BadResponseError class to handle cases where API responses are invalid. This addition enhances error handling
by providing a specific exception for bad API responses.

* Refactor address tests to improve validation and error handling.

Added validation for filter types in the list method to ensure they are lists. Changed error handling to raise
BadResponseError for invalid responses and updated corresponding assertions. Simplified filter parameters by removing
unused names filter.

* Refactor error handling to use BadResponseError

Replaced instances of APIError with BadResponseError in address module and tests. This improves clarity by
distinguishing response format errors from other API-related issues. Updated relevant test cases to reflect this change.

* Refactor tests and enhance error handling in Address module

Reorganized test classes by functionality and added comprehensive error handling tests for create, retrieve, update,
delete, and fetch operations. Improved test coverage by including various exception scenarios and validation checks for
better robustness.

* Refactor address group management for better error handling

Enhanced error handling for address group methods by integrating a custom ErrorHandler. Added detailed docstrings and
implemented client-side filtering. Improved parameter validation and included a delete method.

* Add custom validators for the 'tag' field

Ensure 'tag' is a string or list of strings, and enforce uniqueness within the list. This enhances data integrity and
prevents duplicate entries in the 'tag' field.

* Refactor tests and improve error handling for AddressGroup

Grouped test classes by functionality for better organization. Added more detailed tests for object creation, retrieval,
update, deletion, and fetch, including error handling and validation scenarios. These changes enhance test coverage and
readability.

* Add error handling and client-side filtering for Application

Enhanced the Application class with detailed error handling for API calls, utilizing a custom ErrorHandler. Introduced
client-side filtering for listings and revamped docstrings for better clarity and consistency.

* Refactor test cases for better modularity and error handling

Seperate test classes based on functionality like creation, retrieval, updating, and deletion of `Application` objects.
This also includes enhanced exception handling and validation in the tests for multiple scenarios to improve robustness
and maintainability.

* Refactor ApplicationGroup class for improved error handling

Included custom error handling using the ErrorHandler class across all methods. Enhanced docstrings for better clarity
and added validation checks, especially for empty fields.

* Rename fetch tests for consistency

Renamed `test_fetch_application` and `test_fetch_application_not_found` methods to `test_fetch_object` and
`test_fetch_object_not_found` respectively. This change ensures that the test method names accurately reflect their
purpose of fetching general objects rather than specifically applications.

* Rename application test methods to generic object naming

Refactor test method names in test_application.py to use 'object' instead of 'application' for consistency and clarity.
This change ensures a more generalized approach, making the tests reusable for various object types and easier to
maintain.

* Refactor test method names for simplicity

Renamed several test methods to improve clarity and consistency across the test suite. This change simplifies the method
names by removing redundancy and shortening them, which helps in maintaining and understanding the tests more easily.

* Rename tests and add UUID validation test

Renamed several test method names to improve readability and consistency. Added a new test to check for invalid UUID
format in the response model. Enhanced error handling in list method for multiple container parameters.

* Refactor tests to improve structure and error handling

Restructure the test classes to group them by functionality such as listing, creation, retrieval, updating, and deletion
of Application Group objects. Additionally, enhance error and validation handling in methods dealing with API
interactions to improve code readability and maintainability.

* Add error handling and filtering improvements to Service class

Enhanced the Service class to include comprehensive error handling in the create, get, update, list, fetch, and delete
methods. Added client-side filtering capabilities and detailed validation for incoming parameters.

* Refactor service tests for better modularity and error handling

Grouped service tests by functionality like list, create, get, update, delete, and fetch. Enhanced error handling and
exception raising for various scenarios, ensuring clear and accurate validation of input data and responses.

* Add comprehensive error handling tests for fetch and list methods

Enhanced the test suite for the fetch and list methods by adding various cases for error handling and response
validation. This includes new tests for non-existent objects, unexpected response formats, and invalid filters, ensuring
robust API interactions.

* Update junit.xml schema version

Changed the XML schema version in junit.xml to ensure compatibility with the latest testing framework updates. This
modification addresses potential issues with outdated schema references.

* Update junit.xml formatting

Adjusted the formatting in junit.xml for better readability. No functional changes were made to the file content.

* Refactor UUID handling in Address model.

Updated the 'id' field in the Address model to use UUID type instead of str and removed the custom UUID validator. This
change ensures consistency and leverages Pydantic's built-in UUID validation.

* Add model validation tests for Address objects

Introduced various tests to validate the Address model, including scenarios with missing or multiple type fields,
invalid container formats, and proper UUID verification. Updated existing tests to improve clarity and consistency in
naming conventions.

* Add model validation tests for Address objects

Introduced various tests to validate the Address model, including scenarios with missing or multiple type fields,
invalid container formats, and proper UUID verification. Updated existing tests to improve clarity and consistency in
naming conventions.

* Update tests to use 'objects' terminology globally

Replaces references of 'address' with 'object' in test cases, ensuring consistency in terminology. This includes
updating mock responses, function calls, and assertions to reflect the new terminology.

* Refactor AddressGroupResponseModel id field to UUID

Updated the AddressGroupResponseModel class to use the UUID type for the id field instead of str. This change ensures
stricter type validation and removes the need for a custom UUID validator. Additionally, improved code readability by
importing UUID directly from the uuid module.

* Rename test case methods for clarity in address tests

Refactored method names in TestAddressModelValidation to better reflect their purpose and improve readability. Changed '
test_object_create' prefix to 'test_object_model' in all relevant test functions. This ensures consistency and clarity
when reading and maintaining test code.

* Add comprehensive validation tests and refactor object naming

Introduce detailed validation tests for object models, ensuring accurate error handling and successful creation of valid
models. Refactor method and variable names for consistency and clarity, changing "address_group" to "object" where
applicable.

* Add validation and update tests for application models

Introduced new tests for validating application models, including scenarios for multiple and no containers provided.
Additionally, enhanced existing tests to generalize terminology from 'application' to 'object,' improving code clarity
and consistency.

* Refactor terminology from 'application group' to 'object'

Updated test cases to use a more generic term 'object' instead of 'application group' for better code clarity and
flexibility. Adjusted all relevant variable names, comments, and assertions to match the new terminology.

* Rename variables and comments for consistency

Renamed variables and comments to use "object" instead of "service" for consistency and clarity. This change helps in
maintaining uniform terminology across the test suite, reducing confusion and improving code readability.

* Correct typos in test docstrings

Fixed incorrect usage of 'a' before 'object' in multiple test docstrings, changing it to 'an.' Also corrected the
spelling of 'attempts' in the test for error handling during object updates. These changes improve the readability and
accuracy of the test documentation.

* Add enhanced error handling and filtering to AntiSpywareProfile

Implemented custom error handling across create, get, update, list, and delete methods in the AntiSpywareProfile class.
Introduced client-side filtering for profiles and improved validation for container parameters.

* Rename AntiSpywareProfileRequestModel to AntiSpywareProfileCreateModel

Updated the import in scm/models/security/__init__.py to reflect the new model name. This enhances code clarity and
ensures the correct model is referenced throughout the module.

* Refactor Anti-Spyware Profile models and enums

Reorganize and simplify Anti-Spyware Profile models, including renaming base classes and moving enums to a more
appropriate location. Also added missing field pattern validation and proper docstrings to ensure readability and
maintainability.

* Rename test method for clarity

Renamed `test_object_model_create_no_container` to `test_object_model_no_container_provided` for better readability.
This change clarifies the intent of the test, making it easier to understand what is being validated.

* Update and organize anti-spyware profile tests

Refactor tests in `test_anti_spyware_profile.py` by grouping them according to their functionalities: model validation,
listing, creating, retrieving, updating, deleting, and fetching. Enhance error handling for various scenarios, including
invalid data, missing objects, and malformed requests. Update imports and improve test methods to ensure accurate
validation and error handling.

* Rename anti-spyware factory models to align with new schema

Refactored the `AntiSpywareProfileRequestFactory` and related factory classes to use the updated `CreateModel` schema.
This includes renaming model imports and instances to maintain consistency with the new naming conventions. These
changes help ensure better alignment with the underlying data models.

* Update junit.xml formatting

This commit makes minor formatting changes to the junit.xml file. There are no alterations to the file's content or
functionality. These changes help improve the readability and maintainability of the file's structure.

* Update junit.xml formatting

This commit makes minor formatting changes to the junit.xml file. There are no alterations to the file's content or
functionality. These changes help improve the readability and maintainability of the file's structure.

* Update id field to use UUID type in decryption profiles

Replaced `id` field type from `str` to `UUID` in `DecryptionProfileResponseModel` to ensure proper validation and type
safety. Removed the unnecessary custom validator for `id` field, leveraging Pydantic’s built-in UUID validation.

* Add DecryptionProfileUpdateModel to imports

This commit adds the DecryptionProfileUpdateModel to the imports in the security module initialization. This change
ensures that the update functionalities for decryption profiles are properly included and available for use.

* Update and expand test cases for DecryptionProfile

Refactor test cases in `test_decryption_profile.py` to enhance coverage and clarity. Includes grouped test classes by
functionality, improved error handling tests, detailed docstrings, validation assertions, and expanded mock scenarios
for various API responses and exception handling.

* Update DNS Security Profile functionality with error handling

Enhanced methods to create, update, get, list, and delete DNS Security Profiles with detailed error handling using
custom error classes. Added utility methods for client-side filtering of profiles and constructing parameter
dictionaries. Improved code clarity and consistency in docstrings and exception handling.

* Change id field to UUID in DNSSecurityProfileResponseModel

Converted the `id` field from a string to a UUID in the DNSSecurityProfileResponseModel for better type safety and
accuracy. This also removes the now-unnecessary UUID format validation method.

* Add DNSSecurityProfileUpdateModel import to security module

This change includes the DNSSecurityProfileUpdateModel in the security module's init file. Importing this model is
necessary for handling DNS security profile updates within the module. This ensures that updates to DNS security
profiles are correctly managed and processed.

* Refactor and expand DNS Security Profile tests

Reorganized the test classes for improved readability and maintainability, grouping them by functionality. Expanded the
test coverage to include additional error handling and validation scenarios for create, update, get, delete, and fetch
methods, ensuring robust exception handling and correct API interactions.

* Update security_rule.py for improved functionality and error handling

Refactored the security_rule.py module to enhance clarity and robustness. Introduced custom error handling, expanded
filtering options, and updated models to differentiate between create and update operations. Added built-in constants
and methods for client-side filtering, container parameter construction, and detailed error responses.

* Refactor and optimize security rules models

Consolidate Enums and adjust class structures to enhance clarity and maintainability. Updated validation methods and
field types to ensure robust input handling, and standardized UUID usage across security rules models for better
consistency.

* Add log_setting filter to security_rule

This commit introduces a new filter for `log_setting` in the `security_rule` module. It checks if the `log_setting`
filter is provided and ensures it is a list before filtering. Invalid filter types will raise a `ValidationError`.

* Replace SecurityRuleRequestModel with SecurityRuleCreateModel

Updated the factory and related methods to use SecurityRuleCreateModel instead of SecurityRuleRequestModel. This
includes renaming the factory class methods and updating type hints to match the new model.

* Refactor security rules tests for cleaner structure

Simplified and reorganized the security rules test suite. Grouped and removed redundant tests, streamlined setup
methods, improved fixture utilization, and consolidated duplicate test cases into more efficient structures.

* Add noqa comments to mock responses in security tests

This change adds noqa comments to the dictionary mock responses in the `test_security_rules.py` file. This ensures that
code linters do not flag these lines, allowing tests to run without interruptions or false positives. The integrity of
the mocked data for test validation remains unchanged.

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
