"""Factory definitions for network IPsec Crypto Profile objects."""

import uuid

import factory

from scm.models.network.ipsec_crypto_profile import (
    IPsecCryptoProfileCreateModel,
    IPsecCryptoProfileResponseModel,
    IPsecCryptoProfileUpdateModel,
)


# SDK tests against SCM API
class IPsecCryptoProfileCreateApiFactory(factory.Factory):
    """Factory for creating IPsecCryptoProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for IPsecCryptoProfileCreateApiFactory."""

        model = IPsecCryptoProfileCreateModel

    name = factory.Sequence(lambda n: f"ipsec_crypto_profile_{n}")
    dh_group = "group2"
    lifetime = {"hours": 1}
    lifesize = None
    esp = {"encryption": ["aes-256-cbc"], "authentication": ["sha256"]}
    ah = None
    folder = "Shared"

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Create an instance with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Create an instance with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)


class IPsecCryptoProfileUpdateApiFactory(factory.Factory):
    """Factory for creating IPsecCryptoProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for IPsecCryptoProfileUpdateApiFactory."""

        model = IPsecCryptoProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"ipsec_crypto_profile_{n}")
    dh_group = "group2"
    lifetime = {"hours": 1}
    lifesize = None
    esp = {"encryption": ["aes-256-cbc"], "authentication": ["sha256"]}
    ah = None


class IPsecCryptoProfileResponseFactory(factory.Factory):
    """Factory for creating IPsecCryptoProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for IPsecCryptoProfileResponseFactory."""

        model = IPsecCryptoProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"ipsec_crypto_profile_{n}")
    dh_group = "group2"
    lifetime = {"hours": 1}
    lifesize = None
    esp = {"encryption": ["aes-256-cbc"], "authentication": ["sha256"]}
    ah = None
    folder = "Shared"

    @classmethod
    def from_request(cls, request_model: IPsecCryptoProfileCreateModel, **kwargs):
        """Create a response model based on a request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Pydantic modeling tests
class IPsecCryptoProfileCreateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for IPsecCryptoProfileCreateModel validation testing."""

    name = factory.Sequence(lambda n: f"ipsec_crypto_profile_{n}")
    folder = "Shared"
    lifetime = {"hours": 1}
    esp = {"encryption": ["aes-256-cbc"], "authentication": ["sha256"]}

    @classmethod
    def build_valid(cls):
        """Return a valid data dict with all expected attributes."""
        return cls(
            name="TestIPsecCryptoProfile",
            folder="Shared",
            dh_group="group14",
            lifetime={"hours": 8},
            esp={"encryption": ["aes-256-cbc"], "authentication": ["sha256"]},
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Return a data dict with multiple containers."""
        return cls(
            name="TestIPsecCryptoProfile",
            folder="Shared",
            snippet="TestSnippet",
            lifetime={"hours": 1},
            esp={"encryption": ["aes-256-cbc"], "authentication": ["sha256"]},
        )

    @classmethod
    def build_with_no_container(cls):
        """Return a data dict without any container."""
        return cls(
            name="TestIPsecCryptoProfile",
            folder=None,
            snippet=None,
            device=None,
            lifetime={"hours": 1},
            esp={"encryption": ["aes-256-cbc"], "authentication": ["sha256"]},
        )


class IPsecCryptoProfileUpdateModelFactory(factory.DictFactory):
    """Factory for creating data dicts for IPsecCryptoProfileUpdateModel validation testing."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"ipsec_crypto_profile_{n}")
    lifetime = {"hours": 1}
    esp = {"encryption": ["aes-256-cbc"], "authentication": ["sha256"]}

    @classmethod
    def build_valid(cls):
        """Return a valid data dict for updating an IPsec crypto profile."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedIPsecCryptoProfile",
            dh_group="group19",
            lifetime={"hours": 4},
            esp={"encryption": ["aes-256-cbc"], "authentication": ["sha512"]},
        )
