# tests/scm/models/mobile_agent/test_agent_profiles_models.py

"""Tests for mobile agent agent profiles (application settings) models."""

# External libraries
from pydantic import ValidationError
import pytest

# Local SDK imports
from scm.models.mobile_agent.agent_profiles import (
    AgentProfileOperatingSystem,
    AgentProfilesBaseModel,
    AgentProfilesCreateModel,
    AgentProfilesResponseModel,
    AgentProfilesUpdateModel,
    AgentUI,
    ConnectMethodAppConfig,
    ConnectMethodValue,
    CookieLifetime,
    GatewayChoice,
    GatewayPriority,
    GPAppConfig,
    HipCollection,
    HipMacOsPlistEntry,
    HipWindowsRegistryKey,
    InternalHostDetection,
    SaveUserCredentials,
    ThirdPartyVpnClient,
    TunnelMtuAppConfig,
)
from tests.scm.models.mobile_agent.factories import (
    AgentProfilesBaseModelFactory,
    AgentProfilesCreateModelFactory,
    AgentProfilesResponseModelFactory,
    AgentProfilesUpdateModelFactory,
)


class TestAgentProfileOperatingSystem:
    """Tests for the AgentProfileOperatingSystem enum."""

    def test_enum_values(self):
        """Test that the enum has the expected values."""
        assert AgentProfileOperatingSystem.ANDROID == "Android"
        assert AgentProfileOperatingSystem.CHROME == "Chrome"
        assert AgentProfileOperatingSystem.IOT == "IoT"
        assert AgentProfileOperatingSystem.LINUX == "Linux"
        assert AgentProfileOperatingSystem.MAC == "Mac"
        assert AgentProfileOperatingSystem.WINDOWS == "Windows"
        assert AgentProfileOperatingSystem.WINDOWS_UWP == "WindowsUWP"
        assert AgentProfileOperatingSystem.IOS == "iOS"


class TestSaveUserCredentials:
    """Tests for the SaveUserCredentials enum."""

    def test_enum_values(self):
        """Test that the enum has the expected values."""
        assert SaveUserCredentials.NO == "0"
        assert SaveUserCredentials.YES == "1"
        assert SaveUserCredentials.SAVE_USERNAME_ONLY == "2"
        assert SaveUserCredentials.ONLY_WITH_USER_FINGERPRINT == "3"


class TestThirdPartyVpnClient:
    """Tests for the ThirdPartyVpnClient enum."""

    def test_enum_values(self):
        """Test that the enum has the expected values."""
        assert ThirdPartyVpnClient.PAN_VIRTUAL_ETHERNET_ADAPTER == "PAN Virtual Ethernet Adapter"
        assert (
            ThirdPartyVpnClient.JUNIPER_NETWORK_VIRTUAL_ADAPTER
            == "Juniper Network Virtual Adapter"
        )
        assert ThirdPartyVpnClient.CISCO_SYSTEMS_VPN_ADAPTER == "Cisco Systems VPN Adapter"


class TestConnectMethodValue:
    """Tests for the ConnectMethodValue enum."""

    def test_enum_values(self):
        """Test that the enum has the expected values."""
        assert ConnectMethodValue.USER_LOGON == "user-logon"
        assert ConnectMethodValue.PRE_LOGON == "pre-logon"
        assert ConnectMethodValue.ON_DEMAND == "on-demand"
        assert ConnectMethodValue.PRE_LOGON_THEN_ON_DEMAND == "pre-logon-then-on-demand"


class TestGatewayPriority:
    """Tests for the GatewayPriority enum."""

    def test_enum_values(self):
        """Test that the enum has the expected values."""
        assert GatewayPriority.HIGHEST == "0"
        assert GatewayPriority.HIGH == "1"
        assert GatewayPriority.MEDIUM == "2"
        assert GatewayPriority.LOW == "3"
        assert GatewayPriority.LOWEST == "4"
        assert GatewayPriority.MANUAL_ONLY == "5"


class TestAgentProfilesBaseModel:
    """Tests for AgentProfilesBaseModel validation."""

    def test_base_model_minimal(self):
        """Test that a minimal base model can be created with only a name."""
        model = AgentProfilesBaseModel(name="test-profile")
        assert model.name == "test-profile"
        assert model.folder is None
        assert model.agent_ui is None
        assert model.gateways is None

    def test_base_model_from_factory(self):
        """Test that a base model can be created from the factory."""
        model = AgentProfilesBaseModelFactory()
        assert model.name is not None
        assert model.folder == "Mobile Users"
        assert model.os is not None

    def test_base_model_missing_name(self):
        """Test validation when the required name field is missing."""
        with pytest.raises(ValidationError) as exc_info:
            AgentProfilesBaseModel(folder="Mobile Users")
        assert "name\n  Field required" in str(exc_info.value)

    def test_base_model_invalid_folder(self):
        """Test validation when folder value is invalid."""
        with pytest.raises(ValueError) as exc_info:
            AgentProfilesBaseModel(name="test-profile", folder="Invalid Folder")
        assert "Folder must be 'Mobile Users'" in str(exc_info.value)

    def test_base_model_folder_pattern_validation(self):
        """Test folder pattern validation."""
        with pytest.raises(ValidationError) as exc_info:
            AgentProfilesBaseModel(name="test-profile", folder="Invalid@Folder")
        assert "folder\n  String should match pattern" in str(exc_info.value)

    def test_base_model_extra_field_forbidden(self):
        """Test that unknown fields are rejected."""
        with pytest.raises(ValidationError) as exc_info:
            AgentProfilesBaseModel(name="test-profile", unknown_field="value")
        assert "unknown_field" in str(exc_info.value)

    def test_base_model_nested_structures(self):
        """Test that a fully nested model can be created."""
        data = AgentProfilesCreateModelFactory.build_valid_nested()
        model = AgentProfilesCreateModel(**data)
        assert model.agent_ui.agent_user_override_timeout == 30
        assert model.agent_ui.welcome_page.page == "factory-default"
        assert model.authentication_override.accept_cookie.cookie_lifetime.lifetime_in_hours == 24
        assert model.gateways.external.list[0].choice.fqdn == "gw.example.com"
        assert model.gateways.internal.list[0].choice.ip.ipv4 == "10.0.0.1"
        assert model.gp_app_config.config[0].name == "connect-method"
        assert model.gp_app_config.config[1].name == "tunnel-mtu"
        assert model.hip_collection.custom_checks.mac_os.plist[0].name == "com.example.plist"
        assert model.save_user_credentials == SaveUserCredentials.YES
        assert model.third_party_vpn_clients == [ThirdPartyVpnClient.PAN_VIRTUAL_ETHERNET_ADAPTER]

    def test_base_model_invalid_os_value(self):
        """Test validation when os contains an invalid value."""
        with pytest.raises(ValidationError):
            AgentProfilesBaseModel(name="test-profile", os=["NotAnOS"])

    def test_model_dump_excludes_unset(self):
        """Test that model_dump(exclude_unset=True) only includes set fields."""
        model = AgentProfilesBaseModel(name="test-profile", folder="Mobile Users")
        model_dict = model.model_dump(exclude_unset=True)
        assert model_dict == {"name": "test-profile", "folder": "Mobile Users"}


class TestAgentUI:
    """Tests for AgentUI nested model validation."""

    def test_valid_agent_ui(self):
        """Test that a valid agent UI configuration can be created."""
        model = AgentUI(
            agent_user_override_timeout=0,
            max_agent_user_overrides=25,
            passcode="123456",
            uninstall_password="abcdef",
        )
        assert model.agent_user_override_timeout == 0
        assert model.max_agent_user_overrides == 25

    def test_timeout_out_of_range(self):
        """Test validation when agent_user_override_timeout exceeds the maximum."""
        with pytest.raises(ValidationError):
            AgentUI(agent_user_override_timeout=65536)

    def test_max_overrides_out_of_range(self):
        """Test validation when max_agent_user_overrides exceeds the maximum."""
        with pytest.raises(ValidationError):
            AgentUI(max_agent_user_overrides=26)

    def test_passcode_too_short(self):
        """Test validation when passcode is shorter than the minimum length."""
        with pytest.raises(ValidationError):
            AgentUI(passcode="12345")

    def test_uninstall_password_too_long(self):
        """Test validation when uninstall_password exceeds the maximum length."""
        with pytest.raises(ValidationError):
            AgentUI(uninstall_password="x" * 33)


class TestCookieLifetime:
    """Tests for CookieLifetime nested model validation."""

    def test_valid_lifetimes(self):
        """Test that valid lifetime values can be set."""
        model = CookieLifetime(lifetime_in_days=365)
        assert model.lifetime_in_days == 365

    def test_days_out_of_range(self):
        """Test validation when lifetime_in_days exceeds the maximum."""
        with pytest.raises(ValidationError):
            CookieLifetime(lifetime_in_days=366)

    def test_hours_out_of_range(self):
        """Test validation when lifetime_in_hours exceeds the maximum."""
        with pytest.raises(ValidationError):
            CookieLifetime(lifetime_in_hours=73)

    def test_minutes_out_of_range(self):
        """Test validation when lifetime_in_minutes exceeds the maximum."""
        with pytest.raises(ValidationError):
            CookieLifetime(lifetime_in_minutes=60)


class TestGatewayChoice:
    """Tests for GatewayChoice oneOf validation."""

    def test_fqdn_only(self):
        """Test that a gateway choice with only an FQDN is valid."""
        model = GatewayChoice(fqdn="gw.example.com")
        assert model.fqdn == "gw.example.com"
        assert model.ip is None

    def test_ip_only(self):
        """Test that a gateway choice with only an IP is valid."""
        model = GatewayChoice(ip={"ipv4": "10.0.0.1"})
        assert model.ip.ipv4 == "10.0.0.1"
        assert model.fqdn is None

    def test_both_fqdn_and_ip(self):
        """Test validation when both fqdn and ip are provided."""
        with pytest.raises(ValueError) as exc_info:
            GatewayChoice(fqdn="gw.example.com", ip={"ipv4": "10.0.0.1"})
        assert "Exactly one of 'fqdn' or 'ip'" in str(exc_info.value)

    def test_neither_fqdn_nor_ip(self):
        """Test validation when neither fqdn nor ip is provided."""
        with pytest.raises(ValueError) as exc_info:
            GatewayChoice()
        assert "Exactly one of 'fqdn' or 'ip'" in str(exc_info.value)

    def test_invalid_ipv4_pattern(self):
        """Test validation when ipv4 does not match the allowed pattern."""
        with pytest.raises(ValidationError):
            GatewayChoice(ip={"ipv4": "not-an-ip"})


class TestGPAppConfig:
    """Tests for the GlobalProtect app config discriminated union."""

    def test_connect_method_entry(self):
        """Test that a connect-method entry is parsed into the right model."""
        model = GPAppConfig(config=[{"name": "connect-method", "value": ["pre-logon"]}])
        assert isinstance(model.config[0], ConnectMethodAppConfig)
        assert model.config[0].value == [ConnectMethodValue.PRE_LOGON]

    def test_tunnel_mtu_entry(self):
        """Test that a tunnel-mtu entry is parsed into the right model."""
        model = GPAppConfig(config=[{"name": "tunnel-mtu", "value": [1400]}])
        assert isinstance(model.config[0], TunnelMtuAppConfig)
        assert model.config[0].value == [1400]

    def test_unknown_entry_name(self):
        """Test validation when the app config entry name is unknown."""
        with pytest.raises(ValidationError):
            GPAppConfig(config=[{"name": "unknown-config", "value": ["x"]}])

    def test_connect_method_invalid_value(self):
        """Test validation when the connect method value is not allowed."""
        with pytest.raises(ValidationError):
            GPAppConfig(config=[{"name": "connect-method", "value": ["always-on"]}])

    def test_connect_method_too_many_values(self):
        """Test validation when more than one connect method value is provided."""
        with pytest.raises(ValidationError):
            GPAppConfig(config=[{"name": "connect-method", "value": ["user-logon", "pre-logon"]}])

    def test_tunnel_mtu_out_of_range(self):
        """Test validation when the tunnel MTU is out of range."""
        with pytest.raises(ValidationError):
            GPAppConfig(config=[{"name": "tunnel-mtu", "value": [999]}])
        with pytest.raises(ValidationError):
            GPAppConfig(config=[{"name": "tunnel-mtu", "value": [1421]}])

    def test_tunnel_mtu_empty_value(self):
        """Test validation when the tunnel MTU value list is empty."""
        with pytest.raises(ValidationError):
            GPAppConfig(config=[{"name": "tunnel-mtu", "value": []}])


class TestHipModels:
    """Tests for HIP collection nested models."""

    def test_macos_plist_name_required(self):
        """Test that the name field is required for macOS plist entries."""
        with pytest.raises(ValidationError) as exc_info:
            HipMacOsPlistEntry(key=["k1"])
        assert "name\n  Field required" in str(exc_info.value)

    def test_windows_registry_key_name_required(self):
        """Test that the name field is required for Windows registry key entries."""
        with pytest.raises(ValidationError) as exc_info:
            HipWindowsRegistryKey(registry_value=["v1"])
        assert "name\n  Field required" in str(exc_info.value)

    def test_max_wait_time_out_of_range(self):
        """Test validation when max_wait_time is out of range."""
        with pytest.raises(ValidationError):
            HipCollection(max_wait_time=9)
        with pytest.raises(ValidationError):
            HipCollection(max_wait_time=61)

    def test_valid_hip_collection(self):
        """Test that a valid HIP collection can be created."""
        model = HipCollection(
            collect_hip_data=True,
            max_wait_time=20,
            custom_checks={
                "windows": {"registry_key": [{"name": "HKLM\\Software", "registry_value": ["v"]}]},
            },
            exclusion={"category": [{"name": "antivirus", "vendor": [{"name": "v", "product": ["p"]}]}]},
        )
        assert model.collect_hip_data is True
        assert model.custom_checks.windows.registry_key[0].name == "HKLM\\Software"
        assert model.exclusion.category[0].vendor[0].product == ["p"]


class TestInternalHostDetection:
    """Tests for internal host detection models."""

    def test_valid_host_detection(self):
        """Test that a valid internal host detection can be created."""
        model = InternalHostDetection(hostname="host.example.com", ip_address="10.0.0.1")
        assert model.hostname == "host.example.com"

    def test_invalid_hostname_pattern(self):
        """Test validation when hostname has invalid characters."""
        with pytest.raises(ValidationError):
            InternalHostDetection(hostname="invalid host!")


class TestAgentProfilesCreateModel:
    """Tests for AgentProfilesCreateModel validation."""

    def test_create_model_valid(self):
        """Test that a valid create model can be built."""
        data = AgentProfilesCreateModelFactory.build_valid()
        model = AgentProfilesCreateModel(**data)
        assert model.name == data["name"]
        assert model.folder == "Mobile Users"

    def test_create_model_missing_folder(self):
        """Test validation when folder is missing."""
        data = AgentProfilesCreateModelFactory.build_missing_folder()
        with pytest.raises(ValueError) as exc_info:
            AgentProfilesCreateModel(**data)
        assert "Folder is required" in str(exc_info.value)

    def test_create_model_invalid_folder(self):
        """Test validation when folder is not 'Mobile Users'."""
        data = AgentProfilesCreateModelFactory.build_invalid_folder()
        with pytest.raises(ValueError) as exc_info:
            AgentProfilesCreateModel(**data)
        assert "Folder must be 'Mobile Users'" in str(exc_info.value)


class TestAgentProfilesUpdateModel:
    """Tests for AgentProfilesUpdateModel validation."""

    def test_update_model_valid(self):
        """Test that a valid update model can be built."""
        data = AgentProfilesUpdateModelFactory.build_valid()
        model = AgentProfilesUpdateModel(**data)
        assert model.name == data["name"]
        assert model.folder == "Mobile Users"

    def test_update_model_missing_folder(self):
        """Test validation when folder is missing."""
        data = AgentProfilesUpdateModelFactory.build_missing_folder()
        with pytest.raises(ValueError) as exc_info:
            AgentProfilesUpdateModel(**data)
        assert "Folder is required" in str(exc_info.value)


class TestAgentProfilesResponseModel:
    """Tests for AgentProfilesResponseModel validation."""

    def test_response_model_from_factory(self):
        """Test that a response model can be created from the factory."""
        model = AgentProfilesResponseModelFactory()
        assert model.name is not None
        assert model.folder == "Mobile Users"

    def test_response_model_ignores_extra_fields(self):
        """Test that unknown fields in API responses are ignored."""
        model = AgentProfilesResponseModel(
            name="test-profile",
            folder="Mobile Users",
            some_future_field="ignored",
        )
        assert model.name == "test-profile"
        assert not hasattr(model, "some_future_field")
