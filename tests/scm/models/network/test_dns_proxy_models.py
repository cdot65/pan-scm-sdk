"""Test models for DNS Proxy."""

from uuid import UUID

from pydantic import ValidationError
import pytest

from scm.models.network import (
    DnsProxyBaseModel,
    DnsProxyCache,
    DnsProxyCacheMaxTtl,
    DnsProxyCreateModel,
    DnsProxyDefaultServer,
    DnsProxyDomainServer,
    DnsProxyResponseModel,
    DnsProxyStaticEntry,
    DnsProxyTcpQueries,
    DnsProxyUdpQueries,
    DnsProxyUdpRetries,
    DnsProxyUpdateModel,
)


class TestDnsProxySubModels:
    """Test DNS Proxy sub-model validation."""

    def test_default_server_minimal(self):
        """Test DnsProxyDefaultServer with minimal fields."""
        model = DnsProxyDefaultServer(primary="8.8.8.8")
        assert model.primary == "8.8.8.8"
        assert model.secondary is None
        assert model.inheritance is None

    def test_default_server_all_fields(self):
        """Test DnsProxyDefaultServer with all fields."""
        model = DnsProxyDefaultServer(
            primary="8.8.8.8",
            secondary="8.8.4.4",
            inheritance={"source": "ethernet1/1"},
        )
        assert model.primary == "8.8.8.8"
        assert model.secondary == "8.8.4.4"
        assert model.inheritance["source"] == "ethernet1/1"

    def test_domain_server_minimal(self):
        """Test DnsProxyDomainServer with minimal fields."""
        model = DnsProxyDomainServer(name="rule1", primary="10.0.0.1")
        assert model.name == "rule1"
        assert model.primary == "10.0.0.1"
        assert model.domain_name is None
        assert model.cacheable is None

    def test_domain_server_with_domain_name_alias(self):
        """Test DnsProxyDomainServer domain_name field with alias 'domain-name'."""
        # Test using the Python field name
        model = DnsProxyDomainServer(
            name="rule1",
            primary="10.0.0.1",
            domain_name=["example.com", "test.com"],
        )
        assert model.domain_name == ["example.com", "test.com"]

        # Test serialization uses the alias
        dumped = model.model_dump(by_alias=True)
        assert "domain-name" in dumped
        assert dumped["domain-name"] == ["example.com", "test.com"]

    def test_domain_server_all_fields(self):
        """Test DnsProxyDomainServer with all fields populated."""
        model = DnsProxyDomainServer(
            name="rule1",
            primary="10.0.0.1",
            secondary="10.0.0.2",
            cacheable=True,
            domain_name=["example.com"],
        )
        assert model.name == "rule1"
        assert model.primary == "10.0.0.1"
        assert model.secondary == "10.0.0.2"
        assert model.cacheable is True
        assert model.domain_name == ["example.com"]

    def test_static_entry(self):
        """Test DnsProxyStaticEntry validation."""
        model = DnsProxyStaticEntry(
            name="static1",
            domain="www.example.com",
            address=["1.2.3.4", "5.6.7.8"],
        )
        assert model.name == "static1"
        assert model.domain == "www.example.com"
        assert model.address == ["1.2.3.4", "5.6.7.8"]

    def test_static_entry_missing_required(self):
        """Test DnsProxyStaticEntry with missing required fields."""
        with pytest.raises(ValidationError):
            DnsProxyStaticEntry(name="static1")

    def test_tcp_queries(self):
        """Test DnsProxyTcpQueries validation."""
        model = DnsProxyTcpQueries(enabled=True, max_pending_requests=128)
        assert model.enabled is True
        assert model.max_pending_requests == 128

    def test_tcp_queries_alias(self):
        """Test DnsProxyTcpQueries max-pending-requests alias."""
        model = DnsProxyTcpQueries(enabled=True, max_pending_requests=128)
        dumped = model.model_dump(by_alias=True)
        assert "max-pending-requests" in dumped

    def test_tcp_queries_range_validation(self):
        """Test DnsProxyTcpQueries max_pending_requests range validation."""
        # Below minimum
        with pytest.raises(ValidationError):
            DnsProxyTcpQueries(enabled=True, max_pending_requests=63)

        # Above maximum
        with pytest.raises(ValidationError):
            DnsProxyTcpQueries(enabled=True, max_pending_requests=257)

        # Valid bounds
        model_min = DnsProxyTcpQueries(enabled=True, max_pending_requests=64)
        assert model_min.max_pending_requests == 64

        model_max = DnsProxyTcpQueries(enabled=True, max_pending_requests=256)
        assert model_max.max_pending_requests == 256

    def test_udp_retries(self):
        """Test DnsProxyUdpRetries validation."""
        model = DnsProxyUdpRetries(interval=5, attempts=3)
        assert model.interval == 5
        assert model.attempts == 3

    def test_udp_retries_range_validation(self):
        """Test DnsProxyUdpRetries range validation."""
        # Below minimum
        with pytest.raises(ValidationError):
            DnsProxyUdpRetries(interval=0)

        with pytest.raises(ValidationError):
            DnsProxyUdpRetries(attempts=0)

        # Above maximum
        with pytest.raises(ValidationError):
            DnsProxyUdpRetries(interval=31)

        with pytest.raises(ValidationError):
            DnsProxyUdpRetries(attempts=31)

    def test_udp_queries(self):
        """Test DnsProxyUdpQueries validation."""
        model = DnsProxyUdpQueries(
            retries=DnsProxyUdpRetries(interval=5, attempts=3),
        )
        assert model.retries.interval == 5
        assert model.retries.attempts == 3

    def test_cache_max_ttl(self):
        """Test DnsProxyCacheMaxTtl validation."""
        model = DnsProxyCacheMaxTtl(enabled=True, time_to_live=3600)
        assert model.enabled is True
        assert model.time_to_live == 3600

    def test_cache_max_ttl_alias(self):
        """Test DnsProxyCacheMaxTtl time-to-live alias."""
        model = DnsProxyCacheMaxTtl(enabled=True, time_to_live=3600)
        dumped = model.model_dump(by_alias=True)
        assert "time-to-live" in dumped

    def test_cache_max_ttl_range_validation(self):
        """Test DnsProxyCacheMaxTtl time_to_live range validation."""
        # Below minimum
        with pytest.raises(ValidationError):
            DnsProxyCacheMaxTtl(enabled=True, time_to_live=59)

        # Above maximum
        with pytest.raises(ValidationError):
            DnsProxyCacheMaxTtl(enabled=True, time_to_live=86401)

    def test_cache(self):
        """Test DnsProxyCache validation."""
        model = DnsProxyCache(
            enabled=True,
            cache_edns=True,
            max_ttl=DnsProxyCacheMaxTtl(enabled=True, time_to_live=3600),
        )
        assert model.enabled is True
        assert model.cache_edns is True
        assert model.max_ttl.time_to_live == 3600

    def test_cache_aliases(self):
        """Test DnsProxyCache aliases for cache-edns and max-ttl."""
        model = DnsProxyCache(
            enabled=True,
            cache_edns=True,
            max_ttl=DnsProxyCacheMaxTtl(enabled=True),
        )
        dumped = model.model_dump(by_alias=True)
        assert "cache-edns" in dumped
        assert "max-ttl" in dumped


class TestDnsProxyBaseModel:
    """Test DNS Proxy base model validation."""

    def test_valid_minimal_fields(self):
        """Test valid model with only required fields."""
        model = DnsProxyBaseModel(name="test-proxy", folder="Test Folder")
        assert model.name == "test-proxy"
        assert model.folder == "Test Folder"
        assert model.enabled is None
        assert model.default is None
        assert model.interface is None
        assert model.domain_servers is None
        assert model.static_entries is None
        assert model.tcp_queries is None
        assert model.udp_queries is None
        assert model.cache is None

    def test_valid_all_fields(self):
        """Test valid model with all fields populated."""
        model = DnsProxyBaseModel(
            name="test-proxy",
            folder="Test Folder",
            enabled=True,
            default=DnsProxyDefaultServer(primary="8.8.8.8"),
            interface=["ethernet1/1"],
            domain_servers=[
                DnsProxyDomainServer(
                    name="rule1",
                    primary="10.0.0.1",
                    domain_name=["example.com"],
                )
            ],
            static_entries=[
                DnsProxyStaticEntry(
                    name="static1",
                    domain="www.test.com",
                    address=["1.2.3.4"],
                )
            ],
            tcp_queries=DnsProxyTcpQueries(enabled=True),
            udp_queries=DnsProxyUdpQueries(
                retries=DnsProxyUdpRetries(interval=5, attempts=3),
            ),
            cache=DnsProxyCache(enabled=True),
        )
        assert model.name == "test-proxy"
        assert model.enabled is True
        assert model.default.primary == "8.8.8.8"
        assert model.interface == ["ethernet1/1"]
        assert len(model.domain_servers) == 1
        assert len(model.static_entries) == 1

    def test_missing_name_raises_error(self):
        """Test that missing name field raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            DnsProxyBaseModel(folder="Test Folder")
        assert "name" in str(exc_info.value)

    def test_name_max_length(self):
        """Test name field max_length validation (31 chars)."""
        # Valid at max length
        model = DnsProxyBaseModel(name="A" * 31, folder="Test Folder")
        assert len(model.name) == 31

        # Invalid over max length
        with pytest.raises(ValidationError):
            DnsProxyBaseModel(name="A" * 32, folder="Test Folder")

    def test_container_folder(self):
        """Test model with folder container."""
        model = DnsProxyBaseModel(name="test", folder="MyFolder")
        assert model.folder == "MyFolder"
        assert model.snippet is None
        assert model.device is None

    def test_container_snippet(self):
        """Test model with snippet container."""
        model = DnsProxyBaseModel(name="test", snippet="MySnippet")
        assert model.snippet == "MySnippet"
        assert model.folder is None

    def test_container_device(self):
        """Test model with device container."""
        model = DnsProxyBaseModel(name="test", device="MyDevice")
        assert model.device == "MyDevice"
        assert model.folder is None

    def test_container_max_length(self):
        """Test container field max_length validation."""
        # Valid at max length (64 chars)
        model = DnsProxyBaseModel(name="test", folder="A" * 64)
        assert len(model.folder) == 64

        # Invalid over max length
        with pytest.raises(ValidationError):
            DnsProxyBaseModel(name="test", folder="A" * 65)

    def test_container_pattern_validation(self):
        """Test container field pattern validation."""
        # Valid patterns
        model = DnsProxyBaseModel(name="test", folder="My-Folder_1.0")
        assert model.folder == "My-Folder_1.0"

        # Invalid pattern (special chars)
        with pytest.raises(ValidationError):
            DnsProxyBaseModel(name="test", folder="Folder@#$")

    def test_alias_domain_servers(self):
        """Test domain-servers alias on base model."""
        model = DnsProxyBaseModel(
            name="test",
            folder="Test Folder",
            domain_servers=[
                DnsProxyDomainServer(
                    name="rule1",
                    primary="10.0.0.1",
                    domain_name=["example.com"],
                )
            ],
        )
        dumped = model.model_dump(by_alias=True)
        assert "domain-servers" in dumped

    def test_alias_static_entries(self):
        """Test static-entries alias on base model."""
        model = DnsProxyBaseModel(
            name="test",
            folder="Test Folder",
            static_entries=[
                DnsProxyStaticEntry(
                    name="static1",
                    domain="test.com",
                    address=["1.2.3.4"],
                )
            ],
        )
        dumped = model.model_dump(by_alias=True)
        assert "static-entries" in dumped

    def test_alias_tcp_queries(self):
        """Test tcp-queries alias on base model."""
        model = DnsProxyBaseModel(
            name="test",
            folder="Test Folder",
            tcp_queries=DnsProxyTcpQueries(enabled=True),
        )
        dumped = model.model_dump(by_alias=True)
        assert "tcp-queries" in dumped

    def test_alias_udp_queries(self):
        """Test udp-queries alias on base model."""
        model = DnsProxyBaseModel(
            name="test",
            folder="Test Folder",
            udp_queries=DnsProxyUdpQueries(),
        )
        dumped = model.model_dump(by_alias=True)
        assert "udp-queries" in dumped


class TestDnsProxyCreateModel:
    """Test DNS Proxy create model."""

    def test_valid_create_with_folder(self):
        """Test valid create model with folder container."""
        model = DnsProxyCreateModel(
            name="test-proxy",
            folder="Test Folder",
            enabled=True,
        )
        assert model.name == "test-proxy"
        assert model.folder == "Test Folder"

    def test_valid_create_with_snippet(self):
        """Test valid create model with snippet container."""
        model = DnsProxyCreateModel(
            name="test-proxy",
            snippet="MySnippet",
        )
        assert model.snippet == "MySnippet"

    def test_valid_create_with_device(self):
        """Test valid create model with device container."""
        model = DnsProxyCreateModel(
            name="test-proxy",
            device="MyDevice",
        )
        assert model.device == "MyDevice"

    def test_create_no_container_raises_error(self):
        """Test that create without any container raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            DnsProxyCreateModel(name="test-proxy")
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_multiple_containers_raises_error(self):
        """Test that create with multiple containers raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            DnsProxyCreateModel(
                name="test-proxy",
                folder="Test Folder",
                snippet="MySnippet",
            )
        assert "Exactly one of 'folder', 'snippet', or 'device' must be provided" in str(
            exc_info.value
        )

    def test_create_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on DnsProxyCreateModel."""
        with pytest.raises(ValidationError) as exc_info:
            DnsProxyCreateModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_create_with_default_server(self):
        """Test create model with default server configuration."""
        model = DnsProxyCreateModel(
            name="test-proxy",
            folder="Test Folder",
            default=DnsProxyDefaultServer(
                primary="8.8.8.8",
                secondary="8.8.4.4",
            ),
        )
        assert model.default.primary == "8.8.8.8"
        assert model.default.secondary == "8.8.4.4"

    def test_create_with_domain_servers(self):
        """Test create model with domain server rules and domain_name list validation."""
        model = DnsProxyCreateModel(
            name="test-proxy",
            folder="Test Folder",
            domain_servers=[
                DnsProxyDomainServer(
                    name="rule1",
                    primary="10.0.0.1",
                    domain_name=["example.com", "test.com"],
                )
            ],
        )
        assert len(model.domain_servers) == 1
        assert model.domain_servers[0].domain_name == ["example.com", "test.com"]


class TestDnsProxyUpdateModel:
    """Test DNS Proxy update model."""

    def test_valid_update_model(self):
        """Test valid update model."""
        model = DnsProxyUpdateModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="updated-proxy",
            folder="Test Folder",
            enabled=True,
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "updated-proxy"

    def test_invalid_uuid(self):
        """Test update model with invalid UUID."""
        with pytest.raises(ValidationError):
            DnsProxyUpdateModel(
                id="not-a-uuid",
                name="test",
                folder="Test Folder",
            )

    def test_missing_id_raises_error(self):
        """Test that missing id field raises ValidationError."""
        with pytest.raises(ValidationError):
            DnsProxyUpdateModel(
                name="test",
                folder="Test Folder",
            )


class TestDnsProxyResponseModel:
    """Test DNS Proxy response model."""

    def test_valid_response_model(self):
        """Test valid response model."""
        model = DnsProxyResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="response-proxy",
            folder="Test Folder",
            enabled=True,
        )
        assert model.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert model.name == "response-proxy"

    def test_missing_id_raises_error(self):
        """Test that missing id field raises ValidationError."""
        with pytest.raises(ValidationError):
            DnsProxyResponseModel(
                name="test",
                folder="Test Folder",
            )


class TestExtraFieldsDnsProxy:
    """Tests for extra field handling on DNS Proxy models."""

    def test_base_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on DnsProxyBaseModel."""
        with pytest.raises(ValidationError) as exc_info:
            DnsProxyBaseModel(
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_update_model_extra_fields_forbidden(self):
        """Test that extra fields are rejected on DnsProxyUpdateModel."""
        with pytest.raises(ValidationError) as exc_info:
            DnsProxyUpdateModel(
                id="123e4567-e89b-12d3-a456-426655440000",
                name="test",
                folder="Test Folder",
                unknown_field="should_fail",
            )
        assert "Extra inputs are not permitted" in str(exc_info.value)

    def test_response_model_extra_fields_ignored(self):
        """Test that extra fields are silently ignored on DnsProxyResponseModel."""
        model = DnsProxyResponseModel(
            id="123e4567-e89b-12d3-a456-426655440000",
            name="test",
            folder="Test Folder",
            unknown_field="should_be_ignored",
        )
        assert not hasattr(model, "unknown_field")
