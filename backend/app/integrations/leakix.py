"""LeakIX OSINT integration."""

import httpx
from typing import Any, Dict

from app.integrations.base import BaseOSINTIntegration


class LeakIXIntegration(BaseOSINTIntegration):
    """LeakIX integration for searching leaks by IP and domain."""

    service_name = "leakix"
    rate_limit_calls = 30
    rate_limit_period = 60

    BASE_URL = "https://leakix.net"

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {"accept": "application/json"}
        if self.api_key:
            headers["api-key"] = self.api_key
        return headers

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search leaks by IP or domain."""
        cache_key = f"leakix:search:{query}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/search",
                    headers=self._headers(),
                    params={"q": query, "scope": "leak"},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                result: Dict[str, Any] = {"results": data or [], "count": len(data or []), "query": query}
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
        """Get host or domain details from LeakIX."""
        cache_key = f"leakix:host:{identifier}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/host/{identifier}",
                    headers=self._headers(),
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

    async def get_leaks(self, scope: str) -> Dict[str, Any]:
        """List recent leaks for a given scope (ip, domain, etc.)."""
        cache_key = f"leakix:leaks:{scope}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/search",
                    headers=self._headers(),
                    params={"q": scope, "scope": "leak", "page": 0},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                result: Dict[str, Any] = {"leaks": data or [], "count": len(data or []), "scope": scope}
                self._set_cache(cache_key, result)
                self.log_request("get_leaks", scope, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("get_leaks", scope, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("get_leaks", scope, False)
                return {"error": str(exc), "service": self.service_name}
