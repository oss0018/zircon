"""Intelligence X OSINT integration."""

import httpx
from typing import Any, Dict

from app.integrations.base import BaseOSINTIntegration


class IntelXIntegration(BaseOSINTIntegration):
    """Intelligence X integration for searching emails, domains, IPs, Bitcoin addresses, and CIDR ranges."""

    service_name = "intelx"
    rate_limit_calls = 10
    rate_limit_period = 60

    BASE_URL = "https://2.intelx.io"

    def _headers(self) -> Dict[str, str]:
        return {"x-key": self.api_key}

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search by email, domain, IP, Bitcoin address, or CIDR."""
        cache_key = f"intelx:search:{query}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.BASE_URL}/intelligent/search",
                    headers=self._headers(),
                    json={"term": query, "buckets": [], "lookuplevel": 0, "maxresults": 100, "timeout": 5, "sort": 4, "media": 0, "terminate": []},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                search_id = data.get("id", "")
                result: Dict[str, Any] = {"search_id": search_id, "status": data.get("status", 0), "query": query}
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
        """Get search result details for a given identifier (initiates search)."""
        return await self.search(identifier)

    async def get_results(self, search_id: str, limit: int = 100) -> Dict[str, Any]:
        """Fetch paginated results for an existing search."""
        cache_key = f"intelx:results:{search_id}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/intelligent/search/result",
                    headers=self._headers(),
                    params={"id": search_id, "limit": limit, "offset": 0},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                result: Dict[str, Any] = {
                    "search_id": search_id,
                    "records": data.get("records", []),
                    "count": len(data.get("records", [])),
                    "status": data.get("status", 0),
                }
                self._set_cache(cache_key, result)
                self.log_request("get_results", search_id, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("get_results", search_id, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("get_results", search_id, False)
                return {"error": str(exc), "service": self.service_name}
