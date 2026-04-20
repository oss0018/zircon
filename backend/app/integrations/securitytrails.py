"""SecurityTrails OSINT integration."""

import httpx
from typing import Any, Dict

from app.integrations.base import BaseOSINTIntegration


class SecurityTrailsIntegration(BaseOSINTIntegration):
    """SecurityTrails integration for domain intelligence and DNS history."""

    service_name = "securitytrails"
    rate_limit_calls = 50
    rate_limit_period = 2592000  # ~30 days (free tier: 50/month)

    BASE_URL = "https://api.securitytrails.com/v1"

    def _headers(self) -> Dict[str, str]:
        return {"APIKEY": self.api_key, "Content-Type": "application/json"}

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search domains using SecurityTrails."""
        cache_key = f"securitytrails:search:{query}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.BASE_URL}/domains/list",
                    headers=self._headers(),
                    json={"filter": {"keyword": query}},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                result: Dict[str, Any] = {
                    "records": data.get("records", []),
                    "record_count": data.get("record_count", 0),
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

    async def get_info(self, domain: str, **kwargs) -> Dict[str, Any]:
        """Get domain details including DNS and subdomains."""
        cache_key = f"securitytrails:domain:{domain}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/domain/{domain}",
                    headers=self._headers(),
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
                self._set_cache(cache_key, result)
                self.log_request("get_info", domain, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("get_info", domain, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("get_info", domain, False)
                return {"error": str(exc), "service": self.service_name}

    async def get_subdomains(self, domain: str) -> Dict[str, Any]:
        """List subdomains for a domain."""
        cache_key = f"securitytrails:subdomains:{domain}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/domain/{domain}/subdomains",
                    headers=self._headers(),
                    params={"children_only": "false", "include_inactive": "true"},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                result: Dict[str, Any] = {
                    "domain": domain,
                    "subdomains": data.get("subdomains", []),
                    "count": data.get("subdomain_count", 0),
                }
                self._set_cache(cache_key, result)
                self.log_request("get_subdomains", domain, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("get_subdomains", domain, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("get_subdomains", domain, False)
                return {"error": str(exc), "service": self.service_name}

    async def get_whois(self, domain: str) -> Dict[str, Any]:
        """Get WHOIS data for a domain."""
        cache_key = f"securitytrails:whois:{domain}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/domain/{domain}/whois",
                    headers=self._headers(),
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
                self._set_cache(cache_key, result)
                self.log_request("get_whois", domain, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("get_whois", domain, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("get_whois", domain, False)
                return {"error": str(exc), "service": self.service_name}

    async def get_dns_history(self, domain: str, record_type: str = "a") -> Dict[str, Any]:
        """Get historical DNS records for a domain."""
        cache_key = f"securitytrails:dns_history:{domain}:{record_type}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/history/{domain}/dns/{record_type}",
                    headers=self._headers(),
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                result: Dict[str, Any] = {
                    "domain": domain,
                    "record_type": record_type,
                    "records": data.get("records", []),
                    "pages": data.get("pages", 1),
                }
                self._set_cache(cache_key, result)
                self.log_request("get_dns_history", domain, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("get_dns_history", domain, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("get_dns_history", domain, False)
                return {"error": str(exc), "service": self.service_name}
