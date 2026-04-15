"""urlscan.io OSINT integration."""

import httpx
from typing import Any, Dict

from app.integrations.base import BaseOSINTIntegration


class URLScanIntegration(BaseOSINTIntegration):
    """urlscan.io integration for URL scanning and search."""

    service_name = "urlscan"
    rate_limit_calls = 60
    rate_limit_period = 60

    BASE_URL = "https://urlscan.io/api/v1"

    def _headers(self) -> Dict[str, str]:
        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["API-Key"] = self.api_key
        return headers

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search scans by domain, IP, or hash."""
        cache_key = f"urlscan:search:{query}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/search/",
                    headers=self._headers(),
                    params={"q": query, "size": 100},
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                result: Dict[str, Any] = {
                    "results": data.get("results", []),
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

    async def get_info(self, scan_id: str, **kwargs) -> Dict[str, Any]:
        """Get scan result by scan ID."""
        cache_key = f"urlscan:result:{scan_id}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/result/{scan_id}/",
                    headers=self._headers(),
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
                self._set_cache(cache_key, result)
                self.log_request("get_info", scan_id, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("get_info", scan_id, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("get_info", scan_id, False)
                return {"error": str(exc), "service": self.service_name}

    async def submit_scan(self, url: str, visibility: str = "public") -> Dict[str, Any]:
        """Submit a URL for scanning."""
        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.BASE_URL}/scan/",
                    headers=self._headers(),
                    json={"url": url, "visibility": visibility},
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
                self.log_request("submit_scan", url, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("submit_scan", url, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("submit_scan", url, False)
                return {"error": str(exc), "service": self.service_name}

    async def get_screenshot(self, scan_id: str) -> Dict[str, Any]:
        """Get screenshot URL for a scan."""
        return {
            "scan_id": scan_id,
            "screenshot_url": f"https://urlscan.io/screenshots/{scan_id}.png",
            "thumbnail_url": f"https://urlscan.io/thumbs/{scan_id}.png",
        }
