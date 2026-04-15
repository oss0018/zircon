"""CheckPhish (app.checkphish.ai) OSINT integration.

CheckPhish is a real-time phishing and brand-impersonation detection service.

Rate-limit defaults:
  - 60 requests per minute (starter/free tier)

Scan API (v2):
  POST https://developers.checkphish.ai/api/neo/scan
       body: {"apiKey": "<key>", "urlInfo": {"url": "<url>"}}
  → returns {"jobID": "...", "timestamp": ...}

Status API:
  POST https://developers.checkphish.ai/api/neo/scan/status
       body: {"apiKey": "<key>", "jobID": "<job_id>", "insights": true}
  → returns scan result with disposition, brand, screenshot_path, etc.

Authentication: apiKey in POST JSON body (no Authorization header needed).
"""

import httpx
from typing import Any, Dict

from app.integrations.base import BaseOSINTIntegration


class CheckPhishIntegration(BaseOSINTIntegration):
    """CheckPhish integration for real-time phishing and brand-impersonation detection."""

    service_name = "checkphish"
    # 60 requests per minute (starter tier)
    rate_limit_calls = 60
    rate_limit_period = 60

    BASE_URL = "https://developers.checkphish.ai/api/neo"

    def _api_key_payload(self) -> Dict[str, str]:
        """Return the base payload dict that carries the API key."""
        return {"apiKey": self.api_key}

    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Submit a URL for phishing analysis and return the scan job info.

        ``query`` is expected to be a URL (with or without scheme). A scheme
        is prepended automatically when missing so that CheckPhish can resolve
        the page.
        """
        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        if not self.api_key:
            return {
                "status": "not_configured",
                "service": self.service_name,
                "message": "No API key provided. Set CHECKPHISH_API_KEY in your environment.",
            }

        url = query if "://" in query else f"https://{query}"
        result = await self._submit_scan(url)
        self.log_request("search", query, "error" not in result)
        return result

    async def get_info(self, identifier: str, **kwargs) -> Dict[str, Any]:
        """Retrieve a completed scan result by job ID or re-scan a URL.

        If ``identifier`` looks like a CheckPhish job ID (alphanumeric string),
        the status endpoint is called directly.  Otherwise the identifier is
        treated as a URL and a new scan is submitted.
        """
        cache_key = f"checkphish:info:{identifier}"
        cached = self._get_cached(cache_key)
        if cached is not None:
            return cached

        if not self._check_rate_limit():
            return {"error": "Rate limit exceeded", "service": self.service_name}

        if not self.api_key:
            return {
                "status": "not_configured",
                "service": self.service_name,
                "message": "No API key provided. Set CHECKPHISH_API_KEY in your environment.",
            }

        # Heuristic: job IDs don't contain dots or slashes
        if "." not in identifier and "/" not in identifier and len(identifier) > 8:
            result = await self._get_scan_status(identifier)
        else:
            url = identifier if "://" in identifier else f"https://{identifier}"
            result = await self._submit_scan(url)

        self._set_cache(cache_key, result, ttl=120)
        self.log_request("get_info", identifier, "error" not in result)
        return result

    async def _submit_scan(self, url: str) -> Dict[str, Any]:
        """Submit a URL to CheckPhish for analysis.

        Returns the job metadata (jobID + timestamp) that can be used with
        ``_get_scan_status`` to poll for results.
        """
        payload = {**self._api_key_payload(), "urlInfo": {"url": url}}
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.BASE_URL}/scan",
                    json=payload,
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                return {
                    "service": self.service_name,
                    "action": "scan_submitted",
                    "url": url,
                    "data": data,
                }
            except httpx.HTTPStatusError as exc:
                self.log_request("_submit_scan", url, False)
                return {
                    "error": str(exc),
                    "service": self.service_name,
                    "status_code": exc.response.status_code,
                }
            except httpx.RequestError as exc:
                self.log_request("_submit_scan", url, False)
                return {"error": str(exc), "service": self.service_name}

    async def _get_scan_status(self, job_id: str, insights: bool = True) -> Dict[str, Any]:
        """Poll CheckPhish for the result of a previously submitted scan.

        Args:
            job_id: The job ID returned by ``_submit_scan``.
            insights: When True, request additional brand/screenshot insights.
        """
        payload = {**self._api_key_payload(), "jobID": job_id, "insights": insights}
        async with httpx.AsyncClient() as client:
            try:
                resp = await client.post(
                    f"{self.BASE_URL}/scan/status",
                    json=payload,
                    timeout=30,
                )
                resp.raise_for_status()
                data = resp.json()
                return {
                    "service": self.service_name,
                    "action": "scan_status",
                    "job_id": job_id,
                    "data": data,
                }
            except httpx.HTTPStatusError as exc:
                self.log_request("_get_scan_status", job_id, False)
                return {
                    "error": str(exc),
                    "service": self.service_name,
                    "status_code": exc.response.status_code,
                }
            except httpx.RequestError as exc:
                self.log_request("_get_scan_status", job_id, False)
                return {"error": str(exc), "service": self.service_name}
