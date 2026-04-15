"""PhishTank OSINT integration."""

import httpx
from typing import Any, Dict

from app.integrations.base import BaseOSINTIntegration


class PhishTankIntegration(BaseOSINTIntegration):
    """PhishTank integration for phishing URL verification."""

    service_name = "phishtank"
    rate_limit_calls = 20
    rate_limit_period = 60

    BASE_URL = "https://checkurl.phishtank.com/checkurl/"

    def _headers(self) -> Dict[str, str]:
        return {"User-Agent": "ZirconFRT/1.0"}

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Check if a URL is a known phishing URL."""
        import urllib.parse

        cache_key = f"phishtank:search:{query}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        data: Dict[str, str] = {
            "url": urllib.parse.quote_plus(query),
            "format": "json",
        }
        if self.api_key:
            data["app_key"] = self.api_key

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    self.BASE_URL,
                    headers=self._headers(),
                    data=data,
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
        """Get phishing details for a URL."""
        return await self.search(url)
