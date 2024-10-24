# scm/models/security/__init__.py

from .anti_spyware_profiles import (
    AntiSpywareProfileRequestModel,
    AntiSpywareProfileResponseModel,
)
from .decryption_profiles import (
    DecryptionProfileRequestModel,
    DecryptionProfileResponseModel,
)
from .dns_security_profiles import (
    DNSSecurityProfileRequestModel,
    DNSSecurityProfileResponseModel,
)
from .security_rule_move import SecurityRuleMoveModel
from .security_rules import (
    SecurityRuleRequestModel,
    SecurityRuleResponseModel,
)
from .vulnerability_protection_profiles import (
    VulnerabilityProtectionProfileRequestModel,
    VulnerabilityProtectionProfileResponseModel,
)
from .wildfire_antivirus_profiles import (
    WildfireAntivirusProfileResponseModel,
    WildfireAntivirusProfileRequestModel,
)
