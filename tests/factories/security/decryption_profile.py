"""Factory definitions for decryption profile objects."""

import uuid

import factory

from scm.models.security.decryption_profiles import (
    DecryptionProfileCreateModel,
    DecryptionProfileResponseModel,
    DecryptionProfileUpdateModel,
    SSLForwardProxy,
    SSLInboundProxy,
    SSLNoProxy,
    SSLProtocolSettings,
    SSLVersion,
)


# Sub-factories for component models
class SSLProtocolSettingsFactory(factory.Factory):
    """Factory for SSL protocol settings."""

    class Meta:
        """Meta class that defines the model for SSLProtocolSettingsFactory. It is used by the parent factory SSLProtocolSettingsFactory."""

        model = SSLProtocolSettings

    auth_algo_md5 = True
    auth_algo_sha1 = True
    auth_algo_sha256 = True
    auth_algo_sha384 = True
    enc_algo_3des = True
    enc_algo_aes_128_cbc = True
    enc_algo_aes_256_cbc = True
    enc_algo_aes_128_gcm = True
    enc_algo_aes_256_gcm = True
    min_version = SSLVersion.tls1_0
    max_version = SSLVersion.tls1_2

    @classmethod
    def with_versions(cls, min_ver=SSLVersion.tls1_0, max_ver=SSLVersion.tls1_2, **kwargs):
        """Factory method for creating with SSL versions."""
        return cls(min_version=min_ver, max_version=max_ver, **kwargs)


class SSLForwardProxyFactory(factory.Factory):
    """Factory for SSL forward proxy settings."""

    class Meta:
        """Meta class that defines the model for SSLForwardProxyFactory. It is used by the parent factory SSLForwardProxyFactory."""

        model = SSLForwardProxy

    auto_include_altname = False
    block_client_cert = False
    block_expired_certificate = False
    block_timeout_cert = False
    block_tls13_downgrade_no_resource = False
    block_unknown_cert = False
    block_unsupported_cipher = False
    block_unsupported_version = False
    block_untrusted_issuer = False
    restrict_cert_exts = False
    strip_alpn = False


class SSLInboundProxyFactory(factory.Factory):
    """Factory for creating SSLInboundProxy instances."""

    class Meta:
        """Meta class that defines the model for SSLInboundProxyFactory. It is used by the parent factory SSLInboundProxyFactory."""

        model = SSLInboundProxy

    block_if_hsm_unavailable = False
    block_if_no_resource = False
    block_unsupported_cipher = False
    block_unsupported_version = False


class SSLNoProxyFactory(factory.Factory):
    """Factory for creating SSLNoProxy instances."""

    class Meta:
        """Meta class that defines the model for SSLNoProxyFactory. It is used by the parent factory SSLNoProxyFactory."""

        model = SSLNoProxy

    block_expired_certificate = False
    block_untrusted_issuer = False


# Main factories
class DecryptionProfileCreateApiFactory(factory.Factory):
    """Factory for creating DecryptionProfileCreateModel instances."""

    class Meta:
        """Meta class that defines the model for DecryptionProfileCreateApiFactory. It is used by the parent factory DecryptionProfileCreateApiFactory."""

        model = DecryptionProfileCreateModel

    name = factory.Sequence(lambda n: f"decryption_profile_{n}")
    folder = "Texas"
    ssl_protocol_settings = factory.SubFactory(SSLProtocolSettingsFactory)
    ssl_forward_proxy = factory.SubFactory(SSLForwardProxyFactory)
    ssl_inbound_proxy = factory.SubFactory(SSLInboundProxyFactory)
    ssl_no_proxy = factory.SubFactory(SSLNoProxyFactory)

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Factory method for creating with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Factory method for creating with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def with_custom_ssl_settings(
        cls,
        min_ver: SSLVersion = SSLVersion.tls1_0,
        max_ver: SSLVersion = SSLVersion.tls1_2,
        **kwargs,
    ):
        """Factory method for creating with custom SSL settings."""
        return cls(
            ssl_protocol_settings=SSLProtocolSettingsFactory.with_versions(
                min_ver=min_ver, max_ver=max_ver
            ),
            **kwargs,
        )


class DecryptionProfileUpdateApiFactory(factory.Factory):
    """Factory for creating DecryptionProfileUpdateModel instances."""

    class Meta:
        """Meta class that defines the model for DecryptionProfileUpdateModelFactory."""

        model = DecryptionProfileUpdateModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"decryption_profile_{n}")
    ssl_protocol_settings = factory.SubFactory(SSLProtocolSettingsFactory)
    ssl_forward_proxy = factory.SubFactory(SSLForwardProxyFactory)
    ssl_inbound_proxy = factory.SubFactory(SSLInboundProxyFactory)
    ssl_no_proxy = factory.SubFactory(SSLNoProxyFactory)

    @classmethod
    def with_updated_ssl_settings(cls, **kwargs):
        """Factory method for creating with updated SSL settings."""
        return cls(
            ssl_protocol_settings=SSLProtocolSettingsFactory(
                min_version=SSLVersion.tls1_1,
                max_version=SSLVersion.tls1_3,
            ),
            **kwargs,
        )


class DecryptionProfileResponseFactory(factory.Factory):
    """Factory for creating DecryptionProfileResponseModel instances."""

    class Meta:
        """Meta class that defines the model for DecryptionProfileResponseModelFactory."""

        model = DecryptionProfileResponseModel

    id = factory.LazyFunction(lambda: str(uuid.uuid4()))
    name = factory.Sequence(lambda n: f"decryption_profile_{n}")
    folder = "Texas"
    ssl_protocol_settings = factory.SubFactory(SSLProtocolSettingsFactory)
    ssl_forward_proxy = factory.SubFactory(SSLForwardProxyFactory)
    ssl_inbound_proxy = factory.SubFactory(SSLInboundProxyFactory)
    ssl_no_proxy = factory.SubFactory(SSLNoProxyFactory)

    @classmethod
    def with_snippet(cls, snippet: str = "TestSnippet", **kwargs):
        """Factory method for creating with snippet container."""
        return cls(folder=None, snippet=snippet, device=None, **kwargs)

    @classmethod
    def with_device(cls, device: str = "TestDevice", **kwargs):
        """Factory method for creating with device container."""
        return cls(folder=None, snippet=None, device=device, **kwargs)

    @classmethod
    def from_request(cls, request_model: DecryptionProfileCreateModel, **kwargs):
        """Create response factory from request model."""
        data = request_model.model_dump()
        data["id"] = str(uuid.uuid4())
        data.update(kwargs)
        return cls(**data)


# Dict factories for model validation tests
class DecryptionProfileCreateModelFactory(factory.DictFactory):
    """Factory for creating decryption profile create dictionaries."""

    name = factory.Sequence(lambda n: f"decryption_profile_{n}")
    folder = "Texas"

    @classmethod
    def build_valid(cls):
        """Build valid decryption profile."""
        return cls(
            name="TestProfile",
            folder="Texas",
            ssl_protocol_settings={
                "min_version": "tls1-0",
                "max_version": "tls1-2",
            },
        )

    @classmethod
    def build_with_invalid_name(cls):
        """Build profile with invalid name."""
        return cls(
            name="@invalid-name#",
            folder="Texas",
        )

    @classmethod
    def build_with_invalid_ssl_versions(cls):
        """Build profile with invalid SSL versions."""
        return cls(
            name="TestProfile",
            folder="Texas",
            ssl_protocol_settings={
                "min_version": "tls1-2",
                "max_version": "tls1-0",
            },
        )

    @classmethod
    def build_with_multiple_containers(cls):
        """Build profile with multiple containers."""
        return cls(
            name="TestProfile",
            folder="Texas",
            snippet="TestSnippet",
        )

    @classmethod
    def build_with_no_container(cls):
        """Build profile with no container."""
        return cls(
            name="TestProfile",
            folder=None,
        )


class DecryptionProfileUpdateModelFactory(factory.DictFactory):
    """Factory for creating decryption profile update dictionaries."""

    id = "123e4567-e89b-12d3-a456-426655440000"
    name = factory.Sequence(lambda n: f"decryption_profile_{n}")

    @classmethod
    def build_valid(cls):
        """Build valid decryption profile update."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="UpdatedProfile",
            ssl_protocol_settings={
                "min_version": "tls1-1",
                "max_version": "tls1-3",
            },
        )

    @classmethod
    def build_with_invalid_fields(cls):
        """Build profile with invalid fields."""
        return cls(
            id="invalid-uuid",
            name="@invalid-name#",
            ssl_protocol_settings={
                "min_version": "invalid",
                "max_version": "invalid",
            },
        )

    @classmethod
    def build_minimal_update(cls):
        """Return a data dict with minimal valid update fields."""
        return cls(
            id="123e4567-e89b-12d3-a456-426655440000",
            ssl_forward_proxy={"block_client_cert": True},
        )
