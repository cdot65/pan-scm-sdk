"""Factory definitions for network QoS Profile objects."""

import uuid

import factory

from scm.models.network.qos_profile import (
    QosProfileCreateModel,
    QosProfileResponseModel,
    QosProfileUpdateModel,
)


# SDK tests against SCM API
class QosProfileCreateApiFactory(factory.Factory):
    """Factory for creating QosProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for QosProfileCreateApiFactory."""

        model = QosProfileCreateModel

    name = factory.Sequence(lambda n: f"qos_profile_{n}")
    folder = "Shared"
    aggregate_bandwidth = None
    class_bandwidth_type = None

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_aggregate_bandwidth(cls, **kwargs):
        """Create an instance with aggregate bandwidth settings."""
        return cls(
            aggregate_bandwidth={
                "egress_max": 1000,
                "egress_guaranteed": 500,
            },
            **kwargs,
        )


class QosProfileUpdateApiFactory(factory.Factory):
    """Factory for creating QosProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for QosProfileUpdateApiFactory."""

        model = QosProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"qos_profile_{n}")
    aggregate_bandwidth = None
    class_bandwidth_type = None


class QosProfileResponseFactory(factory.Factory):
    """Factory for creating QosProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for QosProfileResponseFactory."""

        model = QosProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"qos_profile_{n}")
    folder = "Shared"
    aggregate_bandwidth = None
    class_bandwidth_type = None

    @classmethod
    def from_request(cls, request_model: QosProfileCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class QosProfileCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for QosProfileCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"qos_profile_{n}")
    folder = "Shared"

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestQosProfile",
            folder="Shared",
            aggregate_bandwidth={
                "egress_max": 1000,
                "egress_guaranteed": 500,
            },
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestQosProfile",
            folder="Shared",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestQosProfile",
            folder=None,
            snippet=None,
            device=None,
        )


class QosProfileUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for QosProfileUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"qos_profile_{n}")

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating a QoS profile."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedQosProfile",
        )
