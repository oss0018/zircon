"""URLhaus (abuse.ch) OSINT integration."""

import httpx
from typing import Any, Dict, Optional

from app.integrations.base import BaseOSINTIntegration


class URLhausIntegration(BaseOSINTIntegration):
    """URLhaus integration for malicious URL lookups."""

    service_name = "urlhaus"
    rate_limit_calls = 60
    rate_limit_period = 60

    BASE_URL = "https://urlhaus-api.abuse.ch/v1"

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {"Content-Type": "application/x-www-form-urlencoded"}
        if self.api_key:
            headers["Auth-Key"] = self.api_key
        return headers

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search malicious URLs."""
        cache_key = f"urlhaus:search:{query}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.BASE_URL}/url/",
                    headers=self._headers(),
                    data={"url": query},
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

    async def get_info(self, url: str, **kwargs) -> Dict[str, Any]:
        """Get URL information from URLhaus."""
        return await self.search(url)

    async def search_host(self, host: str) -> Dict[str, Any]:
        """Search by hostname or IP."""
        cache_key = f"urlhaus:host:{host}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.BASE_URL}/host/",
                    headers=self._headers(),
                    data={"host": host},
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
                self._set_cache(cache_key, result)
                self.log_request("search_host", host, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("search_host", host, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("search_host", host, False)
                return {"error": str(exc), "service": self.service_name}

    async def search_payload(self, hash_value: str, hash_type: Optional[str] = None) -> Dict[str, Any]:
        """Search by payload hash (md5 or sha256)."""
        cache_key = f"urlhaus:payload:{hash_value}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        # Detect hash type based on length if not provided
        if hash_type is None:
            hash_type = "sha256" if len(hash_value) == 64 else "md5"

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.BASE_URL}/payload/",
                    headers=self._headers(),
                    data={hash_type: hash_value},
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
                self._set_cache(cache_key, result)
                self.log_request("search_payload", hash_value, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("search_payload", hash_value, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("search_payload", hash_value, False)
                return {"error": str(exc), "service": self.service_name}
