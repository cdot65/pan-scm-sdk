# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.4.0] - 2024-12-20

### Added
- Bearer token authentication support for stateless automation scenarios
- New `access_token` parameter in Scm and ScmClient constructors
- Example scripts demonstrating bearer token usage
- Unit and integration tests for bearer token functionality
- Support for Ansible and other automation frameworks

### Changed
- Comprehensive documentation updates for setup services (device, folder, label, snippet, variable)
- All documentation now uses unified ScmClient interface pattern
- Update examples use fetch → dot notation → update workflow
- Added Default column to all model attribute tables
- Added Filter Parameters tables documenting server-side and client-side filters
- Expanded Related Models sections with links to all model types
- Added Variable Types and Enum documentation throughout

### Fixed
- Documentation inconsistencies between config class and model docs
- Corrected parameter types in Core Methods tables

## [0.3.14] - 2025-02-28

### Added
- Unified client interface that allows attribute-based access to services
- New example demonstrating the unified client pattern
- New `ScmClient` class as an alias for `Scm`
- Added comprehensive tests for the unified client functionality

### Changed
- Updated documentation to demonstrate both traditional and unified client patterns
- Updated version number in pyproject.toml

## [0.3.13] - 2025-02-22

### Added
- Support for HTTP Server Profiles
- Integration with CI/CD
- More tests

## [0.3.12] - 2025-02-15

### Fixed
- DNS Security profiles list method fixed

## [0.3.11] - 2025-02-04

### Added
- Added Anti Spyware Profile model
- Improved error handling
- Various bug fixes
