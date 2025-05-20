"""Tag models for Strata Cloud Manager SDK.

Contains Pydantic models for representing tag objects and related data.
"""

# scm/models/objects/tag.py

from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    constr,
    field_validator,
    model_validator,
)

from scm.utils.tag_colors import normalize_color_name

TagString = constr(max_length=127)


class Colors(str, Enum):
    """Enumeration of available color names for tag resources."""

    AZURE_BLUE = "Azure Blue"
    BLACK = "Black"
    BLUE = "Blue"
    BLUE_GRAY = "Blue Gray"
    BLUE_VIOLET = "Blue Violet"
    BROWN = "Brown"
    BURNT_SIENNA = "Burnt Sienna"
    CERULEAN_BLUE = "Cerulean Blue"
    CHESTNUT = "Chestnut"
    COBALT_BLUE = "Cobalt Blue"
    COPPER = "Copper"
    CYAN = "Cyan"
    FOREST_GREEN = "Forest Green"
    GOLD = "Gold"
    GRAY = "Gray"
    GREEN = "Green"
    LAVENDER = "Lavender"
    LIGHT_GRAY = "Light Gray"
    LIGHT_GREEN = "Light Green"
    LIME = "Lime"
    MAGENTA = "Magenta"
    MAHOGANY = "Mahogany"
    MAROON = "Maroon"
    MEDIUM_BLUE = "Medium Blue"
    MEDIUM_ROSE = "Medium Rose"
    MEDIUM_VIOLET = "Medium Violet"
    MIDNIGHT_BLUE = "Midnight Blue"
    OLIVE = "Olive"
    ORANGE = "Orange"
    ORCHID = "Orchid"
    PEACH = "Peach"
    PURPLE = "Purple"
    RED = "Red"
    RED_VIOLET = "Red Violet"
    RED_ORANGE = "Red-Orange"
    SALMON = "Salmon"
    THISTLE = "Thistle"
    TURQUOISE_BLUE = "Turquoise Blue"
    VIOLET_BLUE = "Violet Blue"
    YELLOW = "Yellow"
    YELLOW_ORANGE = "Yellow-Orange"

    @classmethod
    def from_normalized_name(
        cls,
        normalized_name: str,
    ) -> Optional[str]:
        """Retrieve the standard color name based on the normalized color name.

        Args:
            normalized_name (str): The normalized color name.

        Returns:
            Optional[str]: The standard color name if found, else None.

        """
        for color in cls:
            if normalize_color_name(color) == normalized_name:
                return color
        return None


class TagBaseModel(BaseModel):
    """Base model for Tag objects containing fields common to all CRUD operations.

    Attributes:
        name (str): The name of the tag object.
        comments (Optional[str]): The comments of the tag object.
        tag (Optional[List[TagString]]): Tags associated with the tag object.
        folder (Optional[str]): The folder in which the resource is defined.
        snippet (Optional[str]): The snippet in which the resource is defined.
        device (Optional[str]): The device in which the resource is defined.

    """

    # Required fields
    name: str = Field(
        ...,
        max_length=127,
        description="The name of the Tag object",
        pattern=r"^[a-zA-Z0-9_ \.-\[\]\-\&\(\)]+$",
    )
    # Optional fields
    color: Optional[str] = Field(
        None,
        description="Color Associated with Tag",
        examples=["Magenta"],
    )

    comments: Optional[str] = Field(
        None,
        description="The comments of the tag object",
        max_length=1023,
    )

    # Container Types
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

    # Pydantic model configuration
    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
    )

    @field_validator("color")
    def validate_color(
        cls,
        value: Optional[str],
    ) -> Optional[str]:
        """Validate and normalize the color value for a tag.

        Args:
            value (Optional[str]): The color value to validate.

        Returns:
            Optional[str]: The validated and standardized color name, or None.

        Raises:
            ValueError: If the color is not recognized or not in the allowed set.

        """
        if value is None:
            return value
        normalized_name = normalize_color_name(value)
        standard_color_name = Colors.from_normalized_name(normalized_name)
        if standard_color_name is None:
            valid_colors = [color for color in Colors]
            raise ValueError(f"Color must be one of: {', '.join(valid_colors)}")
        return standard_color_name


class TagCreateModel(TagBaseModel):
    """Represents the creation of a new Tag object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for an TagCreateModel object,
    it inherits all fields from the TagBaseModel class, and provides a custom validator
    to ensure that the creation request contains exactly one of the following container types:
        - folder
        - snippet
        - device

    Error:
        ValueError: Raised when container type validation fails.

    """

    # Custom Validators
    @model_validator(mode="after")
    def validate_container_type(self) -> "TagCreateModel":
        """Validate that exactly one container type is provided."""
        container_fields = [
            "folder",
            "snippet",
            "device",
        ]
        provided = [field for field in container_fields if getattr(self, field) is not None]
        if len(provided) != 1:
            raise ValueError("Exactly one of 'folder', 'snippet', or 'device' must be provided.")
        return self


class TagUpdateModel(TagBaseModel):
    """Represents the update of an existing Tag object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for an TagUpdateModel object, similar to the
    TagCreateModel class, but does not have the same custom validator as the TagBaseModel class.

    Creating this dedicated Update model in the event that additional validators or fields are required in the
    near future.
    """

    # Optional fields

    id: Optional[UUID] = Field(
        None,
        description="The UUID of the application group",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )


class TagResponseModel(TagBaseModel):
    """Represents the creation of a new Tag object for Palo Alto Networks' Strata Cloud Manager.

    This class defines the structure and validation rules for an TagResponseModel object,
    it inherits all fields from the TagBaseModel class, adds its own attribute for the
    id field, and provides a custom validator to ensure that it is of the type UUID

    Attributes:
        id (UUID): The UUID of the tag object.

    Error:
        ValueError: Raised when container type validation fails.

    """

    # Optional fields

    id: Optional[UUID] = Field(
        None,
        description="The UUID of the application group",
        examples=["123e4567-e89b-12d3-a456-426655440000"],
    )
