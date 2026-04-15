"""Censys OSINT integration."""

import base64
import httpx
from typing import Any, Dict, Optional

from app.integrations.base import BaseOSINTIntegration


class CensysIntegration(BaseOSINTIntegration):
    """Censys integration for host and certificate searches using Basic auth."""

    service_name = "censys"
    rate_limit_calls = 10
    rate_limit_period = 60

    BASE_URL = "https://search.censys.io/api/v2"

    def __init__(self, api_key: str, api_secret: Optional[str] = None):
        """Initialize with API ID and optional API secret."""
        super().__init__(api_key)
        self.api_secret = api_secret or ""

    def _auth(self) -> httpx.BasicAuth:
        return httpx.BasicAuth(self.api_key, self.api_secret)

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search Censys hosts."""
        cache_key = f"censys:search:{query}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.BASE_URL}/hosts/search",
                    auth=self._auth(),
                    json={"q": query, "per_page": 100},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                result: Dict[str, Any] = {
                    "hits": data.get("result", {}).get("hits", []),
                    "total": data.get("result", {}).get("total", {}).get("value", 0),
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
        """Get host or certificate details by IP or certificate fingerprint."""
        cache_key = f"censys:host:{identifier}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/hosts/{identifier}",
                    auth=self._auth(),
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
                self._set_cache(cache_key, result)
                self.log_request("get_info", identifier, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("get_info", identifier, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("get_info", identifier, False)
                return {"error": str(exc), "service": self.service_name}

    async def search_certificates(self, query: str) -> Dict[str, Any]:
        """Search Censys certificates."""
        cache_key = f"censys:certs:{query}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.BASE_URL}/certificates/search",
                    auth=self._auth(),
                    json={"q": query, "per_page": 100},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                result: Dict[str, Any] = {
                    "hits": data.get("result", {}).get("hits", []),
                    "total": data.get("result", {}).get("total", {}).get("value", 0),
                    "query": query,
                }
                self._set_cache(cache_key, result)
                self.log_request("search_certificates", query, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("search_certificates", query, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("search_certificates", query, False)
                return {"error": str(exc), "service": self.service_name}
