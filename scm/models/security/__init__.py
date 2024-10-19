# scm/models/security/__init__.py

from .anti_spyware_profiles import (
    AntiSpywareProfileRequestModel,
    AntiSpywareProfileResponseModel,
)
from .dns_security_profiles import (
    DNSSecurityProfileRequestModel,
    DNSSecurityProfileResponseModel,
)
from .vulnerability_protection_profiles import (
    VulnerabilityProtectionProfileRequestModel,
    VulnerabilityProtectionProfileResponseModel,
)
from .wildfire_antivirus_profiles import (
    WildfireAntivirusProfileResponseModel,
    WildfireAntivirusProfileRequestModel,
)
