"""Factory definitions for mobile agent Agent Versions objects."""

import factory

from scm.models.mobile_agent.agent_versions import AgentVersionModel, AgentVersionsModel


# SDK tests against SCM API
class AgentVersionModelFactory(factory.Factory):
    """Factory for creating AgentVersionModel instances."""

    class Meta:
        """Meta class that defines the model for AgentVersionModelFactory."""

        model = AgentVersionModel

    version = factory.Sequence(lambda n: f"5.3.{n}")
    release_date = None
    is_recommended = None


class AgentVersionsModelFactory(factory.Factory):
    """Factory for creating AgentVersionsModel instances."""

    class Meta:
        """Meta class that defines the model for AgentVersionsModelFactory."""

        model = AgentVersionsModel

    agent_versions = factory.LazyFunction(lambda: ["5.3.0", "5.2.8", "5.2.7"])


# Pydantic modeling tests
class AgentVersionCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for AgentVersionModel validation testing."""

    version = factory.Sequence(lambda n: f"5.3.{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            version="5.3.0",
            release_date="2023-05-15",
            is_recommended=True,
        )


class AgentVersionsCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for AgentVersionsModel validation testing."""

    agent_versions = ["5.3.0", "5.2.8", "5.2.7"]

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            agent_versions=["5.3.0", "5.2.8", "5.2.7"],
        )
