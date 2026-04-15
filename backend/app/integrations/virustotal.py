"""VirusTotal OSINT integration."""

import httpx
from typing import Any, Dict

from app.integrations.base import BaseOSINTIntegration


class VirusTotalIntegration(BaseOSINTIntegration):
    """VirusTotal integration for URL, domain, IP, and file hash analysis."""

    service_name = "virustotal"
    rate_limit_calls = 4
    rate_limit_period = 60

    BASE_URL = "https://www.virustotal.com/api/v3"

    def _headers(self) -> Dict[str, str]:
        return {"x-apikey": self.api_key}

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Search by URL, domain, IP, or file hash."""
        import base64

        cache_key = f"virustotal:search:{query}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        # Detect type: IP, domain, or URL/hash
        if self._is_ip(query):
            result = await self.get_ip_report(query)
        elif "." in query and "/" not in query and len(query) < 64:
            result = await self.get_domain_report(query)
        else:
            # URL or hash — encode for VirusTotal URL lookup
            url_id = base64.urlsafe_b64encode(query.encode()).rstrip(b"=").decode()
            result = await self.get_info(url_id)

        self._set_cache(cache_key, result)
        self.log_request("search", query, "error" not in result)
        return result

    def _is_ip(self, value: str) -> bool:
        """Heuristic check if value looks like an IP address."""
        parts = value.split(".")
        if len(parts) == 4:
            return all(p.isdigit() and 0 <= int(p) <= 255 for p in parts)
        return False

    async def get_info(self, identifier: str, **kwargs) -> Dict[str, Any]:
        """Get analysis report for a URL ID or file hash."""
        cache_key = f"virustotal:info:{identifier}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/urls/{identifier}",
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

    async def scan_url(self, url: str) -> Dict[str, Any]:
        """Submit a URL for scanning."""
        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.BASE_URL}/urls",
                    headers=self._headers(),
                    data={"url": url},
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
                self.log_request("scan_url", url, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("scan_url", url, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("scan_url", url, False)
                return {"error": str(exc), "service": self.service_name}

    async def get_domain_report(self, domain: str) -> Dict[str, Any]:
        """Get domain report with subdomains and DNS info."""
        cache_key = f"virustotal:domain:{domain}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/domains/{domain}",
                    headers=self._headers(),
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
                self._set_cache(cache_key, result)
                self.log_request("get_domain_report", domain, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("get_domain_report", domain, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("get_domain_report", domain, False)
                return {"error": str(exc), "service": self.service_name}

    async def get_ip_report(self, ip: str) -> Dict[str, Any]:
        """Get IP address report."""
        cache_key = f"virustotal:ip:{ip}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        async with httpx.AsyncClient() as client:
            try:
                resp = await client.get(
                    f"{self.BASE_URL}/ip_addresses/{ip}",
                    headers=self._headers(),
                    timeout=30,
                )
                resp.raise_for_status()
                result = resp.json()
                self._set_cache(cache_key, result)
                self.log_request("get_ip_report", ip, True)
                return result
            except httpx.HTTPStatusError as exc:
                self.log_request("get_ip_report", ip, False)
                return {"error": str(exc), "service": self.service_name}
            except httpx.RequestError as exc:
                self.log_request("get_ip_report", ip, False)
                return {"error": str(exc), "service": self.service_name}
