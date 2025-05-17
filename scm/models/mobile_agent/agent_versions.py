"""Agent Versions models for Strata Cloud Manager SDK.

Contains Pydantic models for representing agent version objects and related data.
"""

# scm/models/mobile_agent/agent_versions.py

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class AgentVersionModel(BaseModel):
    """Model for GlobalProtect agent version.

    This model represents a single agent version in the Strata Cloud Manager API.

    Attributes:
        version (str): The version string of the GlobalProtect agent
        release_date (Optional[str]): The release date of this version
        is_recommended (Optional[bool]): Whether this version is recommended

    """

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
    )

    version: str = Field(
        ...,
        description="The version string of the GlobalProtect agent",
        examples=["5.3.0"],
    )

    release_date: Optional[str] = Field(
        None,
        description="The release date of this version",
        examples=["2023-05-15"],
    )

    is_recommended: Optional[bool] = Field(
        None,
        description="Whether this version is recommended",
        examples=[True],
    )


class AgentVersionsModel(BaseModel):
    """Model for GlobalProtect agent versions.

    GlobalProtect agent versions are read-only resources in the Strata Cloud Manager API,
    only supporting list operations.

    Attributes:
        agent_versions (List[str]): The available versions of the GlobalProtect agent.

    """

    model_config = ConfigDict(
        populate_by_name=True,
        validate_assignment=True,
    )

    agent_versions: List[str] = Field(
        ...,
        description="The available versions of the GlobalProtect agent",
        examples=["5.3.0", "5.2.8", "5.2.7"],
    )
