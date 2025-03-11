# tests/scm/models/network/test_ipsec_crypto_profile_models.py

import pytest
from pydantic import ValidationError
from uuid import UUID

from scm.models.network import (
    IPsecCryptoProfileCreateModel,
    IPsecCryptoProfileUpdateModel,
    IPsecCryptoProfileResponseModel,
    DhGroup,
    EspEncryption,
    AhAuthentication,
    LifetimeSeconds,
    LifetimeMinutes,
    LifetimeHours,
    LifetimeDays,
    LifesizeKB,
    LifesizeMB,
    LifesizeGB,
    LifesizeTB,
    EspConfig,
    AhConfig,
)


class TestIPsecCryptoProfileModels:
    """Tests for IPsec Crypto Profile Pydantic models."""

    def test_lifetime_models(self):
        """Test validation for lifetime models."""
        # Test valid values
        assert LifetimeSeconds(seconds=180).seconds == 180
        assert LifetimeMinutes(minutes=3).minutes == 3
        assert LifetimeHours(hours=1).hours == 1
        assert LifetimeDays(days=1).days == 1

        # Test invalid values
        with pytest.raises(ValidationError):
            LifetimeSeconds(seconds=179)  # Below minimum
        with pytest.raises(ValidationError):
            LifetimeMinutes(minutes=2)  # Below minimum
        with pytest.raises(ValidationError):
            LifetimeHours(hours=0)  # Below minimum
        with pytest.raises(ValidationError):
            LifetimeDays(days=0)  # Below minimum

        with pytest.raises(ValidationError):
            LifetimeSeconds(seconds=65536)  # Above maximum
        with pytest.raises(ValidationError):
            LifetimeMinutes(minutes=65536)  # Above maximum
        with pytest.raises(ValidationError):
            LifetimeHours(hours=65536)  # Above maximum
        with pytest.raises(ValidationError):
            LifetimeDays(days=366)  # Above maximum

    def test_lifesize_models(self):
        """Test validation for lifesize models."""
        # Test valid values
        assert LifesizeKB(kb=1).kb == 1
        assert LifesizeMB(mb=1).mb == 1
        assert LifesizeGB(gb=1).gb == 1
        assert LifesizeTB(tb=1).tb == 1

        # Test invalid values
        with pytest.raises(ValidationError):
            LifesizeKB(kb=0)  # Below minimum
        with pytest.raises(ValidationError):
            LifesizeMB(mb=0)  # Below minimum
        with pytest.raises(ValidationError):
            LifesizeGB(gb=0)  # Below minimum
        with pytest.raises(ValidationError):
            LifesizeTB(tb=0)  # Below minimum

        with pytest.raises(ValidationError):
            LifesizeKB(kb=65536)  # Above maximum
        with pytest.raises(ValidationError):
            LifesizeMB(mb=65536)  # Above maximum
        with pytest.raises(ValidationError):
            LifesizeGB(gb=65536)  # Above maximum
        with pytest.raises(ValidationError):
            LifesizeTB(tb=65536)  # Above maximum

    def test_esp_config(self):
        """Test ESP configuration validation."""
        # Test valid ESP configuration
        esp_config = EspConfig(
            encryption=[EspEncryption.AES_128_CBC, EspEncryption.AES_256_CBC],
            authentication=["sha1", "sha256"],
        )
        assert esp_config.encryption == [EspEncryption.AES_128_CBC, EspEncryption.AES_256_CBC]
        assert esp_config.authentication == ["sha1", "sha256"]

        # Test missing fields
        with pytest.raises(ValidationError):
            EspConfig(encryption=[EspEncryption.AES_128_CBC])  # Missing authentication
        with pytest.raises(ValidationError):
            EspConfig(authentication=["sha1"])  # Missing encryption

    def test_ah_config(self):
        """Test AH configuration validation."""
        # Test valid AH configuration
        ah_config = AhConfig(
            authentication=[AhAuthentication.SHA1, AhAuthentication.SHA256],
        )
        assert ah_config.authentication == [AhAuthentication.SHA1, AhAuthentication.SHA256]

        # Test missing fields
        with pytest.raises(ValidationError):
            AhConfig()  # Missing authentication

    def test_ipsec_crypto_profile_create_model(self):
        """Test IPsecCryptoProfileCreateModel validation."""
        # Test valid ESP-based profile with required fields
        profile = IPsecCryptoProfileCreateModel(
            name="test-esp-profile",
            lifetime={"seconds": 3600},
            esp=EspConfig(
                encryption=[EspEncryption.AES_128_CBC],
                authentication=["sha1"],
            ),
            folder="Test Folder",
        )
        assert profile.name == "test-esp-profile"
        assert profile.lifetime == {"seconds": 3600}
        assert profile.esp.encryption == [EspEncryption.AES_128_CBC]
        assert profile.esp.authentication == ["sha1"]
        assert profile.folder == "Test Folder"
        assert profile.dh_group == DhGroup.GROUP2  # Default value

        # Test valid AH-based profile with required fields
        profile = IPsecCryptoProfileCreateModel(
            name="test-ah-profile",
            lifetime={"hours": 1},
            ah=AhConfig(
                authentication=[AhAuthentication.SHA1],
            ),
            snippet="Test Snippet",
        )
        assert profile.name == "test-ah-profile"
        assert profile.lifetime == {"hours": 1}
        assert profile.ah.authentication == [AhAuthentication.SHA1]
        assert profile.snippet == "Test Snippet"

        # Test valid profile with optional lifesize
        profile = IPsecCryptoProfileCreateModel(
            name="test-profile-with-lifesize",
            lifetime={"minutes": 30},
            lifesize={"gb": 100},
            esp=EspConfig(
                encryption=[EspEncryption.AES_256_CBC],
                authentication=["sha256"],
            ),
            device="Test Device",
        )
        assert profile.name == "test-profile-with-lifesize"
        assert profile.lifetime == {"minutes": 30}
        assert profile.lifesize == {"gb": 100}
        assert profile.device == "Test Device"

        # Test invalid - both ESP and AH provided
        with pytest.raises(ValueError, match="Only one security protocol"):
            IPsecCryptoProfileCreateModel(
                name="invalid-both-protocols",
                lifetime={"seconds": 3600},
                esp=EspConfig(
                    encryption=[EspEncryption.AES_128_CBC],
                    authentication=["sha1"],
                ),
                ah=AhConfig(
                    authentication=[AhAuthentication.SHA1],
                ),
                folder="Test Folder",
            )

        # Test invalid - neither ESP nor AH provided
        with pytest.raises(ValueError, match="At least one security protocol"):
            IPsecCryptoProfileCreateModel(
                name="invalid-no-protocols",
                lifetime={"seconds": 3600},
                folder="Test Folder",
            )

        # Test invalid - multiple container fields provided
        with pytest.raises(ValueError, match="Exactly one of 'folder'"):
            IPsecCryptoProfileCreateModel(
                name="invalid-containers",
                lifetime={"seconds": 3600},
                esp=EspConfig(
                    encryption=[EspEncryption.AES_128_CBC],
                    authentication=["sha1"],
                ),
                folder="Test Folder",
                snippet="Test Snippet",
            )

        # Test invalid - no container fields provided
        with pytest.raises(ValueError, match="Exactly one of 'folder'"):
            IPsecCryptoProfileCreateModel(
                name="invalid-no-container",
                lifetime={"seconds": 3600},
                esp=EspConfig(
                    encryption=[EspEncryption.AES_128_CBC],
                    authentication=["sha1"],
                ),
            )

        # Test invalid name format
        with pytest.raises(ValidationError):
            IPsecCryptoProfileCreateModel(
                name="invalid name!",  # Invalid character !
                lifetime={"seconds": 3600},
                esp=EspConfig(
                    encryption=[EspEncryption.AES_128_CBC],
                    authentication=["sha1"],
                ),
                folder="Test Folder",
            )

    def test_ipsec_crypto_profile_update_model(self):
        """Test IPsecCryptoProfileUpdateModel validation."""
        # Test valid update model
        profile = IPsecCryptoProfileUpdateModel(
            id=UUID("123e4567-e89b-12d3-a456-426655440000"),
            name="updated-profile",
            lifetime={"seconds": 7200},
            esp=EspConfig(
                encryption=[EspEncryption.AES_256_CBC],
                authentication=["sha256"],
            ),
            folder="Updated Folder",
        )
        assert profile.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert profile.name == "updated-profile"
        assert profile.lifetime == {"seconds": 7200}
        assert profile.esp.encryption == [EspEncryption.AES_256_CBC]
        assert profile.folder == "Updated Folder"

        # Test missing ID
        with pytest.raises(ValidationError):
            IPsecCryptoProfileUpdateModel(
                name="missing-id",
                lifetime={"seconds": 3600},
                esp=EspConfig(
                    encryption=[EspEncryption.AES_128_CBC],
                    authentication=["sha1"],
                ),
                folder="Test Folder",
            )

    def test_ipsec_crypto_profile_response_model(self):
        """Test IPsecCryptoProfileResponseModel validation."""
        # Test valid response model
        profile = IPsecCryptoProfileResponseModel(
            id=UUID("123e4567-e89b-12d3-a456-426655440000"),
            name="response-profile",
            lifetime={"seconds": 3600},
            esp=EspConfig(
                encryption=[EspEncryption.AES_128_CBC],
                authentication=["sha1"],
            ),
            folder="Test Folder",
        )
        assert profile.id == UUID("123e4567-e89b-12d3-a456-426655440000")
        assert profile.name == "response-profile"
        assert profile.lifetime == {"seconds": 3600}
        assert profile.esp.encryption == [EspEncryption.AES_128_CBC]
        assert profile.folder == "Test Folder"

        # Test missing ID
        with pytest.raises(ValidationError):
            IPsecCryptoProfileResponseModel(
                name="missing-id",
                lifetime={"seconds": 3600},
                esp=EspConfig(
                    encryption=[EspEncryption.AES_128_CBC],
                    authentication=["sha1"],
                ),
                folder="Test Folder",
            )

    def test_model_serialization(self):
        """Test model serialization to dict/JSON."""
        # Create a profile
        profile = IPsecCryptoProfileCreateModel(
            name="serialization-test",
            lifetime={"seconds": 3600},
            lifesize={"mb": 500},
            dh_group=DhGroup.GROUP14,
            esp=EspConfig(
                encryption=[EspEncryption.AES_256_CBC],
                authentication=["sha256"],
            ),
            folder="Test Folder",
        )

        # Serialize to dict
        profile_dict = profile.model_dump()
        assert profile_dict["name"] == "serialization-test"
        assert profile_dict["lifetime"] == {"seconds": 3600}
        assert profile_dict["lifesize"] == {"mb": 500}
        assert profile_dict["dh_group"] == "group14"
        assert profile_dict["esp"] == {
            "encryption": ["aes-256-cbc"],
            "authentication": ["sha256"],
        }
        assert profile_dict["folder"] == "Test Folder"

        # Serialize with exclude_unset=True
        profile_dict = profile.model_dump(exclude_unset=True)
        assert "snippet" not in profile_dict
        assert "device" not in profile_dict
        assert "ah" not in profile_dict
        
    def test_process_lifetime_and_lifesize_validator(self):
        """Test the process_lifetime_and_lifesize validator directly."""
        from scm.models.network.ipsec_crypto_profile import (
            IPsecCryptoProfileBaseModel,
            LifetimeSeconds,
            LifetimeMinutes,
            LifetimeHours,
            LifetimeDays,
            LifesizeKB,
            LifesizeMB,
            LifesizeGB,
            LifesizeTB,
        )
        
        # Test validator with non-dict input
        values = "not-a-dict"
        result = IPsecCryptoProfileBaseModel.process_lifetime_and_lifesize(values)
        assert result == "not-a-dict"
        
        # Test with no lifetime
        values = {"name": "test", "folder": "folder"}
        result = IPsecCryptoProfileBaseModel.process_lifetime_and_lifesize(values)
        assert result == values
        
        # Test with different lifetime types
        # Test with LifetimeSeconds
        values = {"name": "test", "lifetime": LifetimeSeconds(seconds=3600)}
        result = IPsecCryptoProfileBaseModel.process_lifetime_and_lifesize(values)
        assert result["lifetime"] == {"seconds": 3600}
        
        # Test with LifetimeMinutes
        values = {"name": "test", "lifetime": LifetimeMinutes(minutes=60)}
        result = IPsecCryptoProfileBaseModel.process_lifetime_and_lifesize(values)
        assert result["lifetime"] == {"minutes": 60}
        
        # Test with LifetimeHours
        values = {"name": "test", "lifetime": LifetimeHours(hours=1)}
        result = IPsecCryptoProfileBaseModel.process_lifetime_and_lifesize(values)
        assert result["lifetime"] == {"hours": 1}
        
        # Test with LifetimeDays
        values = {"name": "test", "lifetime": LifetimeDays(days=1)}
        result = IPsecCryptoProfileBaseModel.process_lifetime_and_lifesize(values)
        assert result["lifetime"] == {"days": 1}
        
        # Test with no lifesize
        values = {"name": "test", "lifetime": {"seconds": 3600}}
        result = IPsecCryptoProfileBaseModel.process_lifetime_and_lifesize(values)
        assert result == values
        
        # Test with different lifesize types
        # Test with LifesizeKB
        values = {"name": "test", "lifetime": {"seconds": 3600}, "lifesize": LifesizeKB(kb=1024)}
        result = IPsecCryptoProfileBaseModel.process_lifetime_and_lifesize(values)
        assert result["lifesize"] == {"kb": 1024}
        
        # Test with LifesizeMB
        values = {"name": "test", "lifetime": {"seconds": 3600}, "lifesize": LifesizeMB(mb=10)}
        result = IPsecCryptoProfileBaseModel.process_lifetime_and_lifesize(values)
        assert result["lifesize"] == {"mb": 10}
        
        # Test with LifesizeGB
        values = {"name": "test", "lifetime": {"seconds": 3600}, "lifesize": LifesizeGB(gb=1)}
        result = IPsecCryptoProfileBaseModel.process_lifetime_and_lifesize(values)
        assert result["lifesize"] == {"gb": 1}
        
        # Test with LifesizeTB
        values = {"name": "test", "lifetime": {"seconds": 3600}, "lifesize": LifesizeTB(tb=1)}
        result = IPsecCryptoProfileBaseModel.process_lifetime_and_lifesize(values)
        assert result["lifesize"] == {"tb": 1}
        
        # Test with both lifetime and lifesize already as dictionaries
        values = {
            "name": "test", 
            "lifetime": {"seconds": 3600}, 
            "lifesize": {"mb": 10}
        }
        result = IPsecCryptoProfileBaseModel.process_lifetime_and_lifesize(values)
        assert result == values