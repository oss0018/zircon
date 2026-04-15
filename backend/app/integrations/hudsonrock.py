"""Hudson Rock (Cavalier API) OSINT integration."""

import httpx
from typing import Any, Dict

from app.integrations.base import BaseOSINTIntegration


class HudsonRockIntegration(BaseOSINTIntegration):
    """Hudson Rock Cavalier integration for infostealer data lookups."""

    service_name = "hudsonrock"
    rate_limit_calls = 10
    rate_limit_period = 60

    BASE_URL = "https://cavalier.hudsonrock.com/api/json/v2"

    def _headers(self) -> Dict[str, str]:
        return {"api-key": self.api_key}

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search by email, domain, or username."""
        cache_key = f"hudsonrock:search:{query}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/osint-tools/search-by-login",
                    headers=self._headers(),
                    params={"email": query},
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
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
        """Get infostealer data for an email, domain, or username."""
        cache_key = f"hudsonrock:info:{identifier}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/osint-tools/search-by-domain",
                    headers=self._headers(),
                    params={"domain": identifier},
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
