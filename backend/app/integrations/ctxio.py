"""CTX.io OSINT integration.

CTX.io provides contextual threat intelligence for URLs, domains, and IPs.

Rate-limit defaults:
  - 60 requests per minute (standard tier)

Base URL: https://api.ctx.io/v2
Authentication: Bearer token via Authorization header.
"""

import httpx
from typing import Any, Dict

from app.integrations.base import BaseOSINTIntegration


class CTXioIntegration(BaseOSINTIntegration):
    """CTX.io integration for contextual threat intelligence on URLs, domains, and IPs."""

    service_name = "ctxio"
    # 60 requests per minute (standard free tier)
    rate_limit_calls = 60
    rate_limit_period = 60

    BASE_URL = "https://api.ctx.io/v2"

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search CTX.io for threat context about a URL, domain, or IP.

        Automatically routes to the appropriate endpoint based on the query shape.
        """
        cache_key = f"ctxio:search:{query}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        if not self.api_key:
            return {
                "status": "not_configured",
                "service": self.service_name,
                "message": "No API key provided. Set CTXIO_API_KEY in your environment.",
            }

        # Route based on query shape
        if self._looks_like_ip(query):
            result = await self._lookup("ip", query)
        elif "://" in query or "/" in query:
            result = await self._lookup("url", query)
        else:
            result = await self._lookup("domain", query)

        self._set_cache(cache_key, result)
        self.log_request("search", query, "error" not in result)
        return result

    async def get_info(self, identifier: str, **kwargs) -> Dict[str, Any]:
        """Get detailed threat context for a specific indicator.

        Accepts a URL, domain, or IP address.
        """
        cache_key = f"ctxio:info:{identifier}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        if not self.api_key:
            return {
                "status": "not_configured",
                "service": self.service_name,
                "message": "No API key provided. Set CTXIO_API_KEY in your environment.",
            }

        if self._looks_like_ip(identifier):
            result = await self._lookup("ip", identifier)
        elif "://" in identifier or "/" in identifier:
            result = await self._lookup("url", identifier)
        else:
            result = await self._lookup("domain", identifier)

        self._set_cache(cache_key, result)
        self.log_request("get_info", identifier, "error" not in result)
        return result

    async def _lookup(self, resource_type: str, value: str) -> Dict[str, Any]:
        """Perform a lookup against the CTX.io REST API.

        Args:
            resource_type: One of "ip", "domain", or "url".
            value: The indicator value to look up.
        """
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/{resource_type}",
                    headers=self._headers(),
                    params={"q": value},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                return {
                    "service": self.service_name,
                    "resource_type": resource_type,
                    "query": value,
                    "data": data,
                }
            except httpx.HTTPStatusError as exc:
                self.log_request(f"_lookup:{resource_type}", value, False)
                return {
                    "error": str(exc),
                    "service": self.service_name,
                    "status_code": exc.response.status_code,
                }
            except httpx.RequestError as exc:
                self.log_request(f"_lookup:{resource_type}", value, False)
                return {"error": str(exc), "service": self.service_name}

    @staticmethod
    def _looks_like_ip(value: str) -> bool:
        """Return True if the value resembles an IPv4 address."""
        parts = value.split(".")
        if len(parts) == 4:
            return all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)
        return False
