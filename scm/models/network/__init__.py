# scm/models/network/__init__.py

from .nat_rules import (
    NatRuleCreateModel,
    NatRuleUpdateModel,
    NatRuleResponseModel,
    DynamicIpAndPort,
    StaticIp,
    InterfaceAddress,
    DestinationTranslation,
    DistributionMethod,
    SourceTranslation,
    DynamicIp,
    DnsRewrite,
    DnsRewriteDirection,
)

from .security_zone import (
    SecurityZoneCreateModel,
    SecurityZoneUpdateModel,
    SecurityZoneResponseModel,
    NetworkInterfaceType,
    NetworkConfig,
    UserAcl,
    DeviceAcl,
)

from .ike_crypto_profile import (
    IKECryptoProfileCreateModel,
    IKECryptoProfileUpdateModel,
    IKECryptoProfileResponseModel,
    HashAlgorithm,
    EncryptionAlgorithm,
    DHGroup,
    LifetimeSeconds,
    LifetimeMinutes,
    LifetimeHours,
    LifetimeDays,
)
