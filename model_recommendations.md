# Pydantic Model Review Recommendations

## Overview

This document contains recommendations for ensuring best practices with Pydantic v2 models in the SCM SDK codebase. These recommendations are based on a review of multiple model implementations across the codebase.

## General Observations

- Overall, the codebase follows most Pydantic v2 best practices
- Models are well-structured with proper inheritance patterns (BaseModel → CreateModel/UpdateModel/ResponseModel)
- Field validation is used extensively and properly
- Documentation is thorough with docstrings and descriptions

## Recommendations for Validators

### Field Validators

1. **Use of `@field_validator` with `cls` parameter**

   ✅ **Current Implementation**: The codebase correctly uses `cls` as the first parameter in field validators. This is the correct approach, as field validators are class methods.

   ```python
   @field_validator("tag")
   def validate_tags(cls, v):
       # validation logic
       return v
   ```

   The decorator automatically ensures it's a class method, so adding `@classmethod` is optional in Pydantic v2. The current implementation is correct either way.

2. **Validator Mode Parameter**

   ✅ **Current Implementation**: The codebase uses the `mode` parameter correctly in many cases:

   ```python
   @field_validator("tag", mode="before")
   def ensure_list_of_strings(cls, v):
       # validation logic
       return v
   ```

   📝 **Recommendation**: Ensure consistent use of the `mode` parameter for all field validators. Use `"before"` when you need to pre-process input data before field validation (like converting strings to lists), and `"after"` (default) for validation after type conversion.

### Model Validators

1. **Use of `@model_validator` with `self` parameter**

   ✅ **Current Implementation**: Model validators correctly use `self` as the parameter for `mode="after"` validators:

   ```python
   @model_validator(mode="after")
   def validate_container(self) -> "NatRuleCreateModel":
       # validation logic
       return self
   ```

   This is correct since model validators with `mode="after"` have access to the instantiated model.

2. **Return Type Annotations**

   ✅ **Current Implementation**: Most model validators correctly include return type annotations, which is good practice:

   ```python
   @model_validator(mode="after")
   def validate_container(self) -> "NatRuleCreateModel":
       # validation logic
       return self
   ```

   📝 **Recommendation**: Ensure all model validators include return type annotations for consistency and improved type checking.

## Specific Recommendations

1. **Model Configuration**

   ⚠️ **Observation**: There's some inconsistency in how model configurations are defined:

   In some models:
   ```python
   model_config = ConfigDict(
       populate_by_name=True,
       validate_assignment=True,
       arbitrary_types_allowed=True,
   )
   ```

   In others:
   ```python
   class Config:
       populate_by_name = True
       validate_assignment = True
   ```

   📝 **Recommendation**: Standardize on the `model_config = ConfigDict()` approach, which is the preferred Pydantic v2 pattern. Update any older-style `class Config` implementations.

2. **Validator Method Names**

   ⚠️ **Observation**: There's inconsistency in validator method naming. Some are descriptive (`validate_tags`), while others are more generic (`ensure_list_of_strings`).

   📝 **Recommendation**: Use consistent, descriptive naming patterns for validators:
   - `validate_*` for general validation
   - `ensure_*` for enforcing specific constraints
   - `convert_*` for type conversion

3. **Field Aliasing**

   ✅ **Current Implementation**: The codebase correctly uses `alias` parameter for fields that need Python-safe names:

   ```python
   from_: List[str] = Field(
       default_factory=lambda: ["any"],
       description="Source zone(s)",
       alias="from",
   )
   ```

   This is the correct approach for reserved keywords.

4. **Default Value Factories**

   ✅ **Current Implementation**: The code correctly uses `default_factory` for mutable default values:

   ```python
   tag: List[str] = Field(
       default_factory=list,
       description="The tags associated with the NAT rule",
   )
   ```

   This prevents the shared mutable default value issue.

5. **Type Imports**

   ⚠️ **Observation**: Some files may be using older style type annotations rather than Python 3.10+ syntax.

   📝 **Recommendation**: Use Python 3.10+ type annotation syntax where possible:

   ```python
   # Instead of
   from typing import Optional, List

   # Use native syntax
   list[str] | None
   ```

6. **Validator `mode` Parameter**

   ⚠️ **Observation**: Not all validators explicitly specify the `mode` parameter.

   📝 **Recommendation**: Always explicitly specify the `mode` parameter for clarity, even when using the default:

   ```python
   @field_validator("tag", mode="after")  # "after" is default but being explicit is clearer
   def validate_tags(cls, v):
       # validation logic
       return v
   ```

7. **Consistent Model Structure**

   ✅ **Current Implementation**: The models follow a consistent pattern of BaseModel → CreateModel/UpdateModel/ResponseModel, which is excellent.

   📝 **Recommendation**: Continue this consistent pattern for all new resources.

## Additional Suggestions

1. **Type Annotations Enhancement**

   📝 **Recommendation**: Consider using more specific types from `typing` for improved static analysis:
   - Use `Literal` types for fields with a fixed set of string options
   - Use `TypedDict` for structured dictionary fields
   - Consider adding `Annotated` for additional metadata

2. **Field-level Validation**

   📝 **Recommendation**: Consider moving more validation logic to Field definitions where appropriate:

   ```python
   # Instead of separate validators for checking range
   port: int = Field(..., ge=1, le=65535, description="Port number")
   ```

3. **Documentation Completeness**

   📝 **Recommendation**: Ensure all models have complete docstrings with class-level descriptions and attribute documentation.

## Conclusion

The Pydantic model implementations in the SCM SDK codebase already follow most best practices. The recommendations above are primarily for standardization and consistency across the codebase, rather than addressing critical issues. The use of validators with `cls` vs `self` parameters is correct in the current implementation.
