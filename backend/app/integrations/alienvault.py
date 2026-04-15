"""AlienVault OTX OSINT integration."""

import httpx
from typing import Any, Dict

from app.integrations.base import BaseOSINTIntegration


class AlienVaultIntegration(BaseOSINTIntegration):
    """AlienVault OTX integration for threat intelligence and IOC lookups."""

    service_name = "alienvault"
    rate_limit_calls = 10000
    rate_limit_period = 3600

    BASE_URL = "https://otx.alienvault.com/api/v1"

    def _headers(self) -> Dict[str, str]:
        return {"X-OTX-API-KEY": self.api_key}

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search pulses and IOCs."""
        cache_key = f"alienvault:search:{query}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/search/pulses",
                    headers=self._headers(),
                    params={"q": query, "limit": 20, "page": 1},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                result: Dict[str, Any] = {
                    "results": data.get("results", []),
                    "count": data.get("count", 0),
                    "query": query,
                }
                self._set_cache(cache_key, result)
                self.log_request("search", query, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("search", query, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("search", query, False)
                return {"error": str(exc), "service": self.service_name}

    async def get_info(self, identifier: str, **kwargs) -> Dict[str, Any]:
        """Get indicator details for an IP, domain, or hash."""
        # Determine indicator type
        if self._is_ip(identifier):
            return await self.get_ip_reputation(identifier)
        elif "." in identifier and "/" not in identifier:
            return await self.get_domain_info(identifier)
        else:
            return await self._get_file_info(identifier)

    def _is_ip(self, value: str) -> bool:
        parts = value.split(".")
        if len(parts) == 4:
            return all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)
        return False

    async def get_pulses(self, query: str) -> Dict[str, Any]:
        """Search threat intelligence pulses."""
        return await self.search(query)

    async def get_ip_reputation(self, ip: str) -> Dict[str, Any]:
        """Get IP reputation from AlienVault OTX."""
        cache_key = f"alienvault:ip:{ip}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/indicators/IPv4/{ip}/general",
                    headers=self._headers(),
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
                self._set_cache(cache_key, result)
                self.log_request("get_ip_reputation", ip, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("get_ip_reputation", ip, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("get_ip_reputation", ip, False)
                return {"error": str(exc), "service": self.service_name}

    async def get_domain_info(self, domain: str) -> Dict[str, Any]:
        """Get domain analysis from AlienVault OTX."""
        cache_key = f"alienvault:domain:{domain}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/indicators/domain/{domain}/general",
                    headers=self._headers(),
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
                self._set_cache(cache_key, result)
                self.log_request("get_domain_info", domain, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("get_domain_info", domain, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("get_domain_info", domain, False)
                return {"error": str(exc), "service": self.service_name}

    async def _get_file_info(self, file_hash: str) -> Dict[str, Any]:
        """Get file analysis from AlienVault OTX."""
        cache_key = f"alienvault:file:{file_hash}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/indicators/file/{file_hash}/general",
                    headers=self._headers(),
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
                self._set_cache(cache_key, result)
                self.log_request("_get_file_info", file_hash, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("_get_file_info", file_hash, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("_get_file_info", file_hash, False)
                return {"error": str(exc), "service": self.service_name}
