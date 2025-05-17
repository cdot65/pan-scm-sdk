"""Authentication models for Strata Cloud Manager SDK.

Contains Pydantic models and validators for representing and validating authentication
requests and credentials for the SCM API.
"""

# scm/models/auth.py

from pydantic import BaseModel, Field, field_validator, model_validator


class AuthRequestModel(BaseModel):
    """Represents an authentication request for Palo Alto Network's Strata Cloud Manager.

    This class defines the structure and validation for authentication requests,
    including client credentials, TSG ID, and scope construction.

    Attributes:
        client_id (str): The client ID for authentication.
        client_secret (str): The client secret for authentication.
        tsg_id (str): The TSG ID used for scope construction.
        scope (str, optional): The authentication scope, automatically constructed if not provided.
        token_url (str): The URL for obtaining access tokens.

    Error:
        ValueError: Raised when tsg_id is missing and scope is not provided.

    """

    client_id: str
    client_secret: str
    tsg_id: str
    scope: str = Field(default=None)
    token_url: str = Field(default="https://auth.apps.paloaltonetworks.com/am/oauth2/access_token")

    @model_validator(mode="before")
    def convert_scope(cls, values):
        """Automatically construct the OAuth scope from tsg_id if not provided.

        Args:
            values (dict): Input values to the model.

        Returns:
            dict: Updated values with 'scope' set if it was missing.

        Raises:
            ValueError: If neither 'scope' nor 'tsg_id' is provided.

        """
        if values.get("scope") is None:
            tsg_id = values.get("tsg_id")
            if tsg_id is None:
                raise ValueError("tsg_id is required to construct scope")
            values["scope"] = f"tsg_id:{tsg_id}"
        return values

    @field_validator("scope")
    def validate_scope(cls, v):
        """Validate that the OAuth scope is not an empty string.

        Args:
            v (str): The value of the scope field.

        Returns:
            str: The validated scope value.

        Raises:
            ValueError: If the scope is an empty string.

        """
        if v is not None and v.strip() == "":
            raise ValueError("Scope cannot be empty string")
        return v
