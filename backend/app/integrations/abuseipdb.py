"""AbuseIPDB OSINT integration."""

import httpx
from typing import Any, Dict

from app.integrations.base import BaseOSINTIntegration


class AbuseIPDBIntegration(BaseOSINTIntegration):
    """AbuseIPDB integration for IP reputation and abuse reporting."""

    service_name = "abuseipdb"
    rate_limit_calls = 1000
    rate_limit_period = 86400  # 1000 per day (free tier)

    BASE_URL = "https://api.abuseipdb.com/api/v2"

    def _headers(self) -> Dict[str, str]:
        return {"Key": self.api_key, "Accept": "application/json"}

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Check IP reputation."""
        return await self.get_info(query)

    async def get_info(self, ip: str, **kwargs) -> Dict[str, Any]:
        """Get detailed IP report with abuse confidence score and reports."""
        cache_key = f"abuseipdb:check:{ip}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/check",
                    headers=self._headers(),
                    params={"ipAddress": ip, "maxAgeInDays": 90, "verbose": ""},
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
                self._set_cache(cache_key, result)
                self.log_request("get_info", ip, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("get_info", ip, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("get_info", ip, False)
                return {"error": str(exc), "service": self.service_name}

    async def get_reports(self, ip: str, page: int = 1, per_page: int = 25) -> Dict[str, Any]:
        """Get individual abuse reports for an IP address."""
        cache_key = f"abuseipdb:reports:{ip}:{page}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/reports",
                    headers=self._headers(),
                    params={"ipAddress": ip, "maxAgeInDays": 90, "page": page, "perPage": per_page},
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
                self._set_cache(cache_key, result)
                self.log_request("get_reports", ip, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("get_reports", ip, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("get_reports", ip, False)
                return {"error": str(exc), "service": self.service_name}

    async def check_subnet(self, cidr: str) -> Dict[str, Any]:
        """Check abuse reports for an entire subnet (CIDR)."""
        cache_key = f"abuseipdb:subnet:{cidr}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/check-block",
                    headers=self._headers(),
                    params={"network": cidr, "maxAgeInDays": 90},
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
                self._set_cache(cache_key, result)
                self.log_request("check_subnet", cidr, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("check_subnet", cidr, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("check_subnet", cidr, False)
                return {"error": str(exc), "service": self.service_name}
