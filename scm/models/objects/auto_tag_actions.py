# scm/models/objects/auto_tag_actions.py

# # Standard library imports
# from typing import Optional, List
# from uuid import UUID
#
# # External libraries
# from pydantic import (
#     BaseModel,
#     Field,
#     field_validator,
#     model_validator,
#     ConfigDict,
#     constr,
# )
#
# TagString = constr(max_length=127)
#
#
# class TaggingModel(BaseModel):
#     """
#     Base model for tagging configuration.
#
#     Attributes:
#         target (str): Source or Destination Address, User, X-Forwarded-For Address.
#         action (str): Add or Remove tag option.
#         timeout (Optional[int]): Timeout value in seconds.
#         tags (Optional[List[TagString]]): List of tags to apply.
#     """
#
#     target: str = Field(
#         ...,
#         description="Source or Destination Address, User, X-Forwarded-For Address",
#     )
#     action: str = Field(
#         ...,
#         description="Add or Remove tag option",
#         pattern=r"^(add-tag|remove-tag)$",
#     )
#     timeout: Optional[int] = Field(
#         None,
#         description="Timeout value in seconds",
#     )
#     tags: Optional[List[TagString]] = Field(
#         None,
#         description="List of tags to apply",
#     )
#
#     @field_validator("tags", mode="before")
#     def ensure_list_of_strings(cls, v):  # noqa
#         if isinstance(v, str):
#             return [v]
#         elif isinstance(v, list):
#             return v
#         else:
#             raise ValueError("Tags must be a string or a list of strings")
#
#     @field_validator("tags")
#     def ensure_unique_items(cls, v):  # noqa
#         if v and len(v) != len(set(v)):
#             raise ValueError("List items must be unique")
#         return v
#
#
# class ActionTypeModel(BaseModel):
#     """
#     Model for action type configuration.
#
#     Attributes:
#         tagging (TaggingModel): Tagging configuration settings.
#     """
#
#     tagging: TaggingModel = Field(
#         ...,
#         description="Tagging configuration",
#     )
#
#
# class ActionModel(BaseModel):
#     """
#     Model for individual actions.
#
#     Attributes:
#         name (str): Name of the action.
#         type (ActionTypeModel): Type configuration for the action.
#     """
#
#     name: str = Field(
#         ...,
#         description="Name of the action",
#         max_length=63,
#         pattern=r"^[0-9a-zA-Z._-]+$",
#     )
#     type: ActionTypeModel = Field(
#         ...,
#         description="Type configuration for the action",
#     )
#
#
# class AutoTagActionBaseModel(BaseModel):
#     """
#     Base model for Auto Tag Action objects containing fields common to all CRUD operations.
#
#     Attributes:
#         name (str): Name of the auto tag action.
#         log_type (str): Log type of the resource.
#         description (Optional[str]): Description of the auto tag action.
#         filter (str): Tag based filter defining group membership.
#         send_to_panorama (Optional[bool]): Whether to send to Panorama.
#         quarantine (Optional[bool]): Quarantine option setting.
#         actions (Optional[List[ActionModel]]): List of actions to perform.
#         folder (Optional[str]): The folder in which the resource is defined.
#         snippet (Optional[str]): The snippet in which the resource is defined.
#         device (Optional[str]): The device in which the resource is defined.
#     """
#
#     # Pydantic model configuration
#     model_config = ConfigDict(
#         populate_by_name=True,
#         validate_assignment=True,
#         arbitrary_types_allowed=True,
#     )
#
#     # Required fields
#     name: str = Field(
#         ...,
#         description="Alphanumeric string [ 0-9a-zA-Z._-]",
#         max_length=63,
#         pattern=r"^[0-9a-zA-Z._-]+$",
#     )
#     filter: str = Field(
#         ...,
#         description="Tag based filter defining group membership",
#         max_length=2047,
#     )
#     log_type: str = Field(
#         ...,
#         description="Log type of the resource",
#     )
#
#     # Optional fields
#     description: Optional[str] = Field(
#         None,
#         description="Description of the auto tag action",
#         max_length=1023,
#     )
#     send_to_panorama: Optional[bool] = Field(
#         None,
#         description="Send to Panorama",
#     )
#     quarantine: Optional[bool] = Field(
#         None,
#         description="Quarantine option",
#     )
#     actions: Optional[List[ActionModel]] = Field(
#         None,
#         description="List of actions",
#     )
#
#     # Container Types
#     folder: Optional[str] = Field(
#         None,
#         pattern=r"^[a-zA-Z\d\-_. ]+$",
#         max_length=64,
#         description="The folder in which the resource is defined",
#         examples=["Prisma Access"],
#     )
#     snippet: Optional[str] = Field(
#         None,
#         pattern=r"^[a-zA-Z\d\-_. ]+$",
#         max_length=64,
#         description="The snippet in which the resource is defined",
#         examples=["My Snippet"],
#     )
#     device: Optional[str] = Field(
#         None,
#         pattern=r"^[a-zA-Z\d\-_. ]+$",
#         max_length=64,
#         description="The device in which the resource is defined",
#         examples=["My Device"],
#     )
#
#
# class AutoTagActionCreateModel(AutoTagActionBaseModel):
#     """
#     Represents the creation of a new Auto Tag Action object.
#
#     This class defines the structure and validation rules for an AutoTagActionCreateModel object,
#     it inherits all fields from the AutoTagActionBaseModel class, and provides a custom validator
#     to ensure that the creation request contains exactly one of the following container types:
#         - folder
#         - snippet
#         - device
#
#     Error:
#         ValueError: Raised when container type validation fails.
#     """
#
#     @model_validator(mode="after")
#     def validate_container_type(self) -> "AutoTagActionCreateModel":
#         """Validates that exactly one container type is provided."""
#         container_fields = [
#             "folder",
#             "snippet",
#             "device",
#         ]
#         provided = [
#             field for field in container_fields if getattr(self, field) is not None
#         ]
#         if len(provided) != 1:
#             raise ValueError(
#                 "Exactly one of 'folder', 'snippet', or 'device' must be provided."
#             )
#         return self
#
#
# class AutoTagActionUpdateModel(AutoTagActionBaseModel):
#     """
#     Represents the update of an existing Auto Tag Action object.
#
#     This class defines the structure and validation rules for an AutoTagActionUpdateModel object.
#     """
#
#     id: Optional[UUID] = Field(
#         ...,
#         description="The UUID of the resource",
#         examples=["123e4567-e89b-12d3-a456-426655440000"],
#     )
#
#
# class AutoTagActionResponseModel(AutoTagActionBaseModel):
#     """
#     Represents the response model for Auto Tag Action objects.
#
#     This class defines the structure for an AutoTagActionResponseModel object,
#     it inherits all fields from the AutoTagActionBaseModel class and adds its own
#     attributes for id.
#
#     Attributes:
#         id (UUID): The UUID of the resource.
#     """
#
#     id: UUID = Field(
#         ...,
#         description="The UUID of the resource",
#         examples=["123e4567-e89b-12d3-a456-426655440000"],
#     )
