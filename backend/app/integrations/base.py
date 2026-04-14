"""Abstract base class for OSINT integrations."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class BaseOSINTIntegration(ABC):
    """Abstract base for all OSINT service integrations."""

    service_name: str = ""
    rate_limit_calls: int = 100
    rate_limit_period: int = 3600  # seconds

    def __init__(self, api_key: str):
        """Initialize the integration with an API key."""
        self.api_key = api_key
        self._call_count = 0
        self._period_start = datetime.utcnow()
        self._cache: Dict[str, Any] = {}

    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits."""
        now = datetime.utcnow()
        if now - self._period_start > timedelta(seconds=self.rate_limit_period):
            self._call_count = 0
            self._period_start = now

        if self._call_count >= self.rate_limit_calls:
            logger.warning(f"Rate limit reached for {self.service_name}")
            return False

        self._call_count += 1
        return True

    def _get_cached(self, key: str) -> Optional[Any]:
        """Get a cached result."""
        entry = self._cache.get(key)
        if entry and datetime.utcnow() < entry["expires"]:
            return entry["data"]
        return None

    def _set_cache(self, key: str, data: Any, ttl: int = 300) -> None:
        """Cache a result with TTL."""
        self._cache[key] = {
            "data": data,
            "expires": datetime.utcnow() + timedelta(seconds=ttl),
        }

    @abstractmethod
    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Perform a search query against the OSINT service."""
        pass

    @abstractmethod
    async def get_info(self, identifier: str, **kwargs) -> Dict[str, Any]:
        """Get information about a specific identifier (IP, domain, hash, etc.)."""
        pass

    def log_request(self, method: str, query: str, success: bool) -> None:
        """Log an API request."""
        status = "success" if success else "failure"
        logger.info(f"[{self.service_name}] {method}({query!r}) -> {status}")
