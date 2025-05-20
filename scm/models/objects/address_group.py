"""Address Group models for Strata Cloud Manager SDK.

Contains Pydantic models for representing address group objects and related data.
"""

# scm/models/objects/address_group.py

from typing import List, Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    constr,
    field_validator,
    model_validator,
)

TagString = constr(max_length=127)


class DynamicFilter(BaseModel):
    """Represents the dynamic filter for an Address Group in Palo Alto Networks' Strata Cloud Manager.

    Attributes:
        filter (str): Tag-based filter defining group membership.

    """

    filter: str = Field(
        ...,
        max_length=1024,
        description="Tag based filter defining group membership",
        examples=["'aws.ec2.key.Name.value.scm-test-scm-test-vpc'"],
    )


class AddressGroupBaseModel(BaseModel):
    """Base model for Address Group objects containing fields common to all CRUD operations.

    Attributes:
        name (str): The name of the address group.
        description (Optional[str]): The description of the address group.
        tag (Optional[List[TagString]]): Tags associated with the address group.
        dynamic (Optional[DynamicFilter]): Dynamic filter defining group membership.
        static (Optional[List[str]]): List of static addresses in the group.
        folder (Optional[str]): The folder in which the resource is defined.
        snippet (Optional[str]): The snippet in which the resource is defined.
        device (Optional[str]): The device in which the resource is defined.

    """

    model_config = ConfigDict(
        validate_assignment=True,
        arbitrary_types_allowed=True,
        populate_by_name=True,
    )

    name: str = Field(
        ...,
        max_length=63,
        description="The name of the address group",
        pattern=r"^[a-zA-Z0-9_ \.-]+$",
    )
    description: Optional[str] = Field(
        None,
        max_length=1023,
        description="The description of the address group",
    )
    tag: Optional[List[TagString]] = Field(  # type: ignore
        None,
        description="Tags associated with the address group",
    )
    dynamic: Optional[DynamicFilter] = Field(
        None,
        description="Dynamic filter defining group membership",
    )
    static: Optional[List[str]] = Field(
        None,
        description="Container type of Static Address Group",
        min_length=1,
        max_length=2048,
        examples=["database-servers"],
    )
    folder: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The folder in which the resource is defined",
        examples=["Prisma Access"],
    )
    snippet: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The snippet in which the resource is defined",
        examples=["My Snippet"],
    )
    device: Optional[str] = Field(
        None,
        pattern=r"^[a-zA-Z\d\-_. ]+$",
        max_length=64,
        description="The device in which the resource is defined",
        examples=["My Device"],
    )

    # Custom Validators
    @field_validator("tag", mode="before")
    def ensure_list_of_strings(cls, v):  # noqa
        if isinstance(v, str):
            return [v]
        elif isinstance(v, list):
            return v
        else:
            raise ValueError("Tag must be a string or a list of strings")

    @field_validator("tag")
    def ensure_unique_items(cls, v):  # noqa
        """Ensure all items in the list are unique.

        Args:
            v (list): The list to validate.

        Returns:
            list: The validated list.

        Raises:
            ValueError: If duplicate items are found.

        """
        if len(v) != len(set(v)):
            raise ValueError("List items must be unique")
        return v

    @model_validator(mode="after")
    def validate_address_group_type(self) -> "AddressGroupBaseModel":
        """Ensure exactly one group type field (dynamic or static) is set.

        Returns:
            AddressGroupBaseModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one group type field is set.

        """
        group_type_fields = ["dynamic", "static"]
        provided = [field for field in group_type_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'static' or 'dynamic' must be provided.")
        return self


class AddressGroupCreateModel(AddressGroupBaseModel):
    """Model for creating a new Address Group.

    Inherits from AddressGroupBase and adds container type validation.
    """

    @model_validator(mode="after")
    def validate_container_type(self) -> "AddressGroupCreateModel":
        """Ensure exactly one container field (folder, snippet, or device) is set.

        Returns:
            AddressGroupCreateModel: The validated model instance.

        Raises:
            ValueError: If zero or more than one container field is set.

        """
        container_fields = ["folder", "snippet", "device"]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class AddressGroupUpdateModel(AddressGroupBaseModel):
    """Model for updating an existing Address Group.

    All fields are optional to allow partial updates.
    """

    id: Optional[str] = Field(
        ...,  # This makes it optional
        description="The UUID of the address object",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class AddressGroupResponseModel(AddressGroupBaseModel):
    """Represents the creation of a new AddressGroup object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for an AddressGroupResponseModel object,
    it inherits all fields from the AddressGroupBaseModel class, adds its own attribute for the
    id field, and provides a custom validator to ensure that it is of the type UUID

    Attributes:
        id (UUID): The UUID of the address object.

    Error:
        ValueError: Raised when container type validation fails.

    """

    id: UUID = Field(
        ...,
        description="The UUID of the application group",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
