# Claude Code Rules Update Summary

This document summarizes the updates made to Claude Code rules based on the review of `sdk_service_file_styling.md`.

## Key Additions from sdk_service_file_styling.md

### 1. Emphasis on Google-style Docstrings
- Explicitly specified that all docstrings must be Google-style
- Added requirement for Args, Returns, and Raises sections

### 2. Boolean Field Handling
- Added critical SCM API requirement: Only include `True` values in payloads
- Must omit `False` values from API payloads
- Always use `.model_dump(exclude_unset=True)` for serialization

### 3. Absolute Imports Only
- Clarified that all SDK-internal imports must be absolute
- No relative imports allowed within the SDK

### 4. Inline Comments Guidelines
- Added specific guidance for inline comments
- Emphasis on explaining validation logic and API workflows
- Document SCM API-specific behaviors

### 5. Line Length Specification
- Explicitly stated 88 characters (ruff default)
- Previously not specified in original files

### 6. Error Handling Details
- Emphasized always using SDK custom exceptions
- Requirement for detailed error codes and messages
- Context must be provided in the `details` dictionary

## Files Updated

1. **CLAUDE.md**
   - Added section on Comments and Documentation
   - Updated Special Behaviors section with boolean handling
   - Enhanced error handling patterns
   - Clarified absolute imports requirement

2. **SDK_STYLING_GUIDE.md**
   - Added Key Conventions section
   - Expanded Special Cases & Behaviors
   - Added more common mistakes to avoid
   - Clarified Google-style docstring requirement

3. **SDK_SERVICE_TEMPLATE.py**
   - Added comments about SCM API requirements
   - Clarified serialization patterns
   - Noted absolute imports requirement

## Key Principles Reinforced

1. **Consistency**: All service files must follow the same patterns
2. **Documentation**: Google-style docstrings are mandatory
3. **API Compatibility**: Boolean handling and serialization must follow SCM API requirements
4. **Error Handling**: Always use SDK custom exceptions with detailed context
5. **Code Quality**: Follow ruff linting standards with 88-character line length

These updates ensure that Claude Code has comprehensive guidance for generating SDK service files that are consistent with both the existing codebase and the formal styling conventions.
