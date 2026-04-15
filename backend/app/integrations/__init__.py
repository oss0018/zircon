"""OSINT Integration Registry — registers and manages all available integrations.

Registered services (15 total):
  Breach & Leaks    : hibp, intelx, leakix, hudsonrock
  Phishing & Malware: virustotal, urlhaus, phishtank, urlscan, ctxio, checkphish
  Infrastructure    : shodan, censys, securitytrails
  Threat Intel      : abuseipdb, alienvault
"""

from typing import Dict, List, Optional, Type

from app.integrations.base import BaseOSINTIntegration


class IntegrationRegistry:
    """Registry of all available OSINT integrations."""

    _integrations: Dict[str, Type[BaseOSINTIntegration]] = {}

    @classmethod
    def register(cls, name: str, integration_class: Type[BaseOSINTIntegration]) -> None:
        """Register an integration class under the given name."""
        cls._integrations[name] = integration_class

    @classmethod
    def get(cls, name: str) -> Optional[Type[BaseOSINTIntegration]]:
        """Return the integration class for the given name, or None."""
        return cls._integrations.get(name)

    @classmethod
    def list_available(cls) -> List[str]:
        """Return a list of all registered integration names."""
        return list(cls._integrations.keys())

    @classmethod
    def create_instance(cls, name: str, api_key: str, **kwargs) -> BaseOSINTIntegration:
        """Create and return an instance of the named integration."""
        integration_class = cls._integrations.get(name)
        if integration_class is None:
            raise ValueError(f"Unknown integration: {name!r}. Available: {cls.list_available()}")
        return integration_class(api_key=api_key, **kwargs)


# ---------------------------------------------------------------------------
# Auto-register all 12 integrations
# ---------------------------------------------------------------------------

from app.integrations.hibp import HIBPIntegration  # noqa: E402
from app.integrations.intelx import IntelXIntegration  # noqa: E402
from app.integrations.leakix import LeakIXIntegration  # noqa: E402
from app.integrations.hudsonrock import HudsonRockIntegration  # noqa: E402
from app.integrations.virustotal import VirusTotalIntegration  # noqa: E402
from app.integrations.urlhaus import URLhausIntegration  # noqa: E402
from app.integrations.phishtank import PhishTankIntegration  # noqa: E402
from app.integrations.urlscan import URLScanIntegration  # noqa: E402
from app.integrations.shodan_integration import ShodanIntegration  # noqa: E402
from app.integrations.censys import CensysIntegration  # noqa: E402
from app.integrations.securitytrails import SecurityTrailsIntegration  # noqa: E402
from app.integrations.abuseipdb import AbuseIPDBIntegration  # noqa: E402
from app.integrations.alienvault import AlienVaultIntegration  # noqa: E402
from app.integrations.ctxio import CTXioIntegration  # noqa: E402
from app.integrations.checkphish import CheckPhishIntegration  # noqa: E402

IntegrationRegistry.register("hibp", HIBPIntegration)
IntegrationRegistry.register("intelx", IntelXIntegration)
IntegrationRegistry.register("leakix", LeakIXIntegration)
IntegrationRegistry.register("hudsonrock", HudsonRockIntegration)
IntegrationRegistry.register("virustotal", VirusTotalIntegration)
IntegrationRegistry.register("urlhaus", URLhausIntegration)
IntegrationRegistry.register("phishtank", PhishTankIntegration)
IntegrationRegistry.register("urlscan", URLScanIntegration)
IntegrationRegistry.register("shodan", ShodanIntegration)
IntegrationRegistry.register("censys", CensysIntegration)
IntegrationRegistry.register("securitytrails", SecurityTrailsIntegration)
IntegrationRegistry.register("abuseipdb", AbuseIPDBIntegration)
IntegrationRegistry.register("alienvault", AlienVaultIntegration)
IntegrationRegistry.register("ctxio", CTXioIntegration)
IntegrationRegistry.register("checkphish", CheckPhishIntegration)

__all__ = [
    "IntegrationRegistry",
    "HIBPIntegration",
    "IntelXIntegration",
    "LeakIXIntegration",
    "HudsonRockIntegration",
    "VirusTotalIntegration",
    "URLhausIntegration",
    "PhishTankIntegration",
    "URLScanIntegration",
    "ShodanIntegration",
    "CensysIntegration",
    "SecurityTrailsIntegration",
    "AbuseIPDBIntegration",
    "AlienVaultIntegration",
    "CTXioIntegration",
    "CheckPhishIntegration",
]
