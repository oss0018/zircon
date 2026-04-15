"""Shodan OSINT integration (named shodan_integration to avoid conflict with the shodan package)."""

import httpx
from typing import Any, Dict

from app.integrations.base import BaseOSINTIntegration


class ShodanIntegration(BaseOSINTIntegration):
    """Shodan integration for device and infrastructure searches."""

    service_name = "shodan"
    rate_limit_calls = 60  # 1 per second effectively, using 60/min
    rate_limit_period = 60

    BASE_URL = "https://api.shodan.io"

    def _params(self) -> Dict[str, str]:
        return {"key": self.api_key}

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search Shodan by query string."""
        cache_key = f"shodan:search:{query}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                params = {**self._params(), "query": query}
                resp = await client.get(
                    f"{self.BASE_URL}/shodan/host/search",
                    params=params,
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                result: Dict[str, Any] = {
                    "matches": data.get("matches", []),
                    "total": data.get("total", 0),
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

    async def get_info(self, ip: str, **kwargs) -> Dict[str, Any]:
        """Get host information for an IP address."""
        cache_key = f"shodan:host:{ip}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/shodan/host/{ip}",
                    params=self._params(),
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

    async def get_ports(self, ip: str) -> Dict[str, Any]:
        """Get open ports for an IP address."""
        info = await self.get_info(ip)
        if "error" in info:
            return info
        return {
            "ip": ip,
            "ports": info.get("ports", []),
            "hostnames": info.get("hostnames", []),
        }

    async def search_dns(self, domain: str) -> Dict[str, Any]:
        """DNS lookup for a domain."""
        cache_key = f"shodan:dns:{domain}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/dns/resolve",
                    params={**self._params(), "hostnames": domain},
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
                self._set_cache(cache_key, result)
                self.log_request("search_dns", domain, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("search_dns", domain, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("search_dns", domain, False)
                return {"error": str(exc), "service": self.service_name}
