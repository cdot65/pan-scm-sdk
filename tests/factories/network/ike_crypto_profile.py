"""Factory definitions for network IKE Crypto Profile objects."""

import uuid

import factory

from scm.models.network.ike_crypto_profile import (
    IKECryptoProfileCreateModel,
    IKECryptoProfileResponseModel,
    IKECryptoProfileUpdateModel,
)


# SDK tests against SCM API
class IKECryptoProfileCreateApiFactory(factory.Factory):
    """Factory for creating IKECryptoProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for IKECryptoProfileCreateApiFactory."""

        model = IKECryptoProfileCreateModel

    name = factory.Sequence(lambda n: f"ike_crypto_profile_{n}")
    hash = ["sha256"]
    encryption = ["aes-256-cbc"]
    dh_group = ["group14"]
    lifetime = None
    authentication_multiple = 0
    folder = "Shared"

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class IKECryptoProfileUpdateApiFactory(factory.Factory):
    """Factory for creating IKECryptoProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for IKECryptoProfileUpdateApiFactory."""

        model = IKECryptoProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"ike_crypto_profile_{n}")
    hash = ["sha256"]
    encryption = ["aes-256-cbc"]
    dh_group = ["group14"]
    lifetime = None
    authentication_multiple = 0


class IKECryptoProfileResponseFactory(factory.Factory):
    """Factory for creating IKECryptoProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for IKECryptoProfileResponseFactory."""

        model = IKECryptoProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"ike_crypto_profile_{n}")
    hash = ["sha256"]
    encryption = ["aes-256-cbc"]
    dh_group = ["group14"]
    lifetime = None
    authentication_multiple = 0
    folder = "Shared"

    @classmethod
    def from_request(cls, request_model: IKECryptoProfileCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class IKECryptoProfileCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for IKECryptoProfileCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"ike_crypto_profile_{n}")
    folder = "Shared"
    hash = ["sha256"]
    encryption = ["aes-256-cbc"]
    dh_group = ["group14"]

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestIKECryptoProfile",
            folder="Shared",
            hash=["sha256", "sha384"],
            encryption=["aes-256-cbc"],
            dh_group=["group14", "group19"],
            authentication_multiple=0,
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestIKECryptoProfile",
            folder="Shared",
            snippet="TestSnippet",
            hash=["sha256"],
            encryption=["aes-256-cbc"],
            dh_group=["group14"],
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestIKECryptoProfile",
            folder=None,
            snippet=None,
            device=None,
            hash=["sha256"],
            encryption=["aes-256-cbc"],
            dh_group=["group14"],
        )


class IKECryptoProfileUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for IKECryptoProfileUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"ike_crypto_profile_{n}")
    hash = ["sha256"]
    encryption = ["aes-256-cbc"]
    dh_group = ["group14"]

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating an IKE crypto profile."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedIKECryptoProfile",
            hash=["sha512"],
            encryption=["aes-256-cbc"],
            dh_group=["group20"],
        )
