"""Have I Been Pwned (HIBP) OSINT integration."""

import httpx
from typing import Any, Dict

from app.integrations.base import BaseOSINTIntegration


class HIBPIntegration(BaseOSINTIntegration):
    """Have I Been Pwned integration for breach and paste monitoring."""

    service_name = "hibp"
    rate_limit_calls = 10
    rate_limit_period = 60

    BASE_URL = "https://haveibeenpwned.com/api/v3"
    USER_AGENT = "ZirconFRT/1.0"

    def _headers(self) -> Dict[str, str]:
        return {
            "hibp-api-key": self.api_key,
            "user-agent": self.USER_AGENT,
        }

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search breaches by email address."""
        cache_key = f"hibp:search:{query}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/breachedaccount/{query}",
                    headers=self._headers(),
                    params={"truncateResponse": "false"},
                    timeout=30,
                )
                if resp.status_code == 404:
                    result: Dict[str, Any] = {"breaches": [], "count": 0}
                else:
                    resp.raise_for_status()
                    data = resp.json()
                    result = {"breaches": data, "count": len(data)}
                self._set_cache(cache_key, result)
                self.log_request("search", query, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("search", query, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("search", query, False)
                return {"error": str(exc), "service": self.service_name}

    async def get_info(self, email: str, **kwargs) -> Dict[str, Any]:
        """Get all breaches for an email."""
        return await self.search(email)

    async def get_pastes(self, email: str) -> Dict[str, Any]:
        """Get pastes for an email address."""
        cache_key = f"hibp:pastes:{email}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/pasteaccount/{email}",
                    headers=self._headers(),
                    timeout=30,
                )
                if resp.status_code == 404:
                    result: Dict[str, Any] = {"pastes": [], "count": 0}
                else:
                    resp.raise_for_status()
                    data = resp.json()
                    result = {"pastes": data, "count": len(data)}
                self._set_cache(cache_key, result)
                self.log_request("get_pastes", email, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("get_pastes", email, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("get_pastes", email, False)
                return {"error": str(exc), "service": self.service_name}

    async def get_breach_details(self, breach_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific breach."""
        cache_key = f"hibp:breach:{breach_name}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/breach/{breach_name}",
                    headers=self._headers(),
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
                self._set_cache(cache_key, result)
                self.log_request("get_breach_details", breach_name, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("get_breach_details", breach_name, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("get_breach_details", breach_name, False)
                return {"error": str(exc), "service": self.service_name}
