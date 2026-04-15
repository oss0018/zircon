"""Integration service — orchestrates OSINT queries across multiple services."""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations import IntegrationRegistry
from app.models.integration import Integration
from app.services.encryption import decrypt_value

logger = logging.getLogger(__name__)


# Metadata for each registered service
SERVICE_INFO: Dict[str, Dict[str, Any]] = {
    "hibp": {
        "name": "Have I Been Pwned",
        "description": "Check if email addresses have been compromised in data breaches.",
        "category": "Breach & Leaks",
        "supported_query_types": ["search", "info", "pastes", "breach_details"],
        "rate_limits": "10 requests/minute",
        "requires_key": True,
    },
    "intelx": {
        "name": "Intelligence X",
        "description": "Search dark web leaks, Tor, I2P, and public data sources.",
        "category": "Breach & Leaks",
        "supported_query_types": ["search", "info", "results"],
        "rate_limits": "10 requests/minute",
        "requires_key": True,
    },
    "leakix": {
        "name": "LeakIX",
        "description": "Search exposed servers and leaked databases.",
        "category": "Breach & Leaks",
        "supported_query_types": ["search", "info", "leaks"],
        "rate_limits": "30 requests/minute",
        "requires_key": False,
    },
    "hudsonrock": {
        "name": "Hudson Rock",
        "description": "Infostealer data for compromised credentials.",
        "category": "Breach & Leaks",
        "supported_query_types": ["search", "info"],
        "rate_limits": "10 requests/minute",
        "requires_key": True,
    },
    "virustotal": {
        "name": "VirusTotal",
        "description": "Analyze URLs, domains, IPs, and file hashes with 70+ antivirus engines.",
        "category": "Phishing & Malware",
        "supported_query_types": ["search", "info", "scan", "domain", "ip"],
        "rate_limits": "4 requests/minute (free tier)",
        "requires_key": True,
    },
    "urlhaus": {
        "name": "URLhaus",
        "description": "Search malicious URLs and payloads from abuse.ch.",
        "category": "Phishing & Malware",
        "supported_query_types": ["search", "info", "host", "payload"],
        "rate_limits": "60 requests/minute",
        "requires_key": False,
    },
    "phishtank": {
        "name": "PhishTank",
        "description": "Verify whether a URL is a known phishing site.",
        "category": "Phishing & Malware",
        "supported_query_types": ["search", "info"],
        "rate_limits": "20 requests/minute",
        "requires_key": False,
    },
    "urlscan": {
        "name": "urlscan.io",
        "description": "Scan and analyse websites for malicious content.",
        "category": "Phishing & Malware",
        "supported_query_types": ["search", "info", "scan", "screenshot"],
        "rate_limits": "60 requests/minute",
        "requires_key": False,
    },
    "shodan": {
        "name": "Shodan",
        "description": "Search internet-connected devices, open ports, and services.",
        "category": "Infrastructure",
        "supported_query_types": ["search", "info", "ports", "dns"],
        "rate_limits": "1 request/second",
        "requires_key": True,
    },
    "censys": {
        "name": "Censys",
        "description": "Search internet-wide scan data for hosts and certificates.",
        "category": "Infrastructure",
        "supported_query_types": ["search", "info", "certificates"],
        "rate_limits": "10 requests/minute (free tier)",
        "requires_key": True,
    },
    "securitytrails": {
        "name": "SecurityTrails",
        "description": "Historical DNS records, WHOIS, and subdomain enumeration.",
        "category": "Infrastructure",
        "supported_query_types": ["search", "info", "subdomains", "whois", "dns_history"],
        "rate_limits": "50 requests/month (free tier)",
        "requires_key": True,
    },
    "abuseipdb": {
        "name": "AbuseIPDB",
        "description": "IP reputation and abuse report database.",
        "category": "Threat Intelligence",
        "supported_query_types": ["search", "info", "reports", "subnet"],
        "rate_limits": "1000 requests/day (free tier)",
        "requires_key": True,
    },
    "alienvault": {
        "name": "AlienVault OTX",
        "description": "Open threat intelligence community with pulses and IOCs.",
        "category": "Threat Intelligence",
        "supported_query_types": ["search", "info", "pulses", "ip", "domain"],
        "rate_limits": "10000 requests/hour",
        "requires_key": True,
    },
}


async def get_user_integration(
    db: AsyncSession, user_id: str, service_name: str
) -> Optional[Integration]:
    """Fetch a user's integration record for a given service."""
    result = await db.execute(
        select(Integration).where(
            Integration.user_id == user_id,
            Integration.service_name == service_name,
            Integration.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def execute_query(
    db: AsyncSession,
    user_id: str,
    service_name: str,
    query: str,
    query_type: str = "search",
    extra_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute a single OSINT query against a service.

    Returns a dict with results, cache flag, timestamp, and credits_used.
    """
    extra_params = extra_params or {}
    start = datetime.now(timezone.utc)

    integration_record = await get_user_integration(db, user_id, service_name)
    api_key = ""
    if integration_record:
        try:
            api_key = decrypt_value(integration_record.encrypted_api_key)
        except Exception as exc:
            logger.error(f"Failed to decrypt API key for {service_name}: {exc}")
            return {
                "service_name": service_name,
                "results": None,
                "cached": False,
                "timestamp": start.isoformat(),
                "credits_used": 0,
                "error": "Failed to decrypt API key",
            }

    try:
        instance = IntegrationRegistry.create_instance(service_name, api_key=api_key, **extra_params)
    except ValueError as exc:
        return {
            "service_name": service_name,
            "results": None,
            "cached": False,
            "timestamp": start.isoformat(),
            "credits_used": 0,
            "error": str(exc),
        }

    try:
        if query_type == "search":
            results = await instance.search(query, **extra_params)
        elif query_type == "info":
            results = await instance.get_info(query, **extra_params)
        elif query_type == "scan":
            if hasattr(instance, "scan_url"):
                results = await instance.scan_url(query)
            elif hasattr(instance, "submit_scan"):
                results = await instance.submit_scan(query)
            else:
                results = await instance.search(query, **extra_params)
        else:
            results = await instance.search(query, **extra_params)
    except Exception as exc:
        logger.error(f"Error executing query on {service_name}: {exc}")
        results = {"error": str(exc)}

    end = datetime.now(timezone.utc)
    elapsed_ms = int((end - start).total_seconds() * 1000)

    logger.info(
        f"[integration_service] user={user_id} service={service_name} "
        f"query_type={query_type} query={query!r} elapsed_ms={elapsed_ms}"
    )

    return {
        "service_name": service_name,
        "results": results,
        "cached": False,
        "timestamp": start.isoformat(),
        "credits_used": 1,
        "elapsed_ms": elapsed_ms,
    }


async def execute_multi_query(
    db: AsyncSession,
    user_id: str,
    service_names: List[str],
    query: str,
    query_type: str = "search",
    extra_params: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute queries against multiple services in parallel.

    Returns aggregated results and any per-service errors.
    """
    extra_params = extra_params or {}
    start = datetime.now(timezone.utc)

    tasks = [
        execute_query(db, user_id, svc, query, query_type, extra_params)
        for svc in service_names
    ]
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    results: Dict[str, Any] = {}
    errors: Dict[str, str] = {}

    for svc, resp in zip(service_names, responses):
        if isinstance(resp, Exception):
            errors[svc] = str(resp)
        elif isinstance(resp, dict) and "error" in resp and resp.get("results") is None:
            errors[svc] = resp["error"]
        else:
            results[svc] = resp

    end = datetime.now(timezone.utc)
    total_time_ms = int((end - start).total_seconds() * 1000)

    return {
        "results": results,
        "errors": errors,
        "total_time_ms": total_time_ms,
        "timestamp": start.isoformat(),
    }


def list_services() -> List[Dict[str, Any]]:
    """Return metadata for all registered services."""
    available = IntegrationRegistry.list_available()
    return [
        {
            "name": svc,
            **SERVICE_INFO.get(svc, {
                "description": "",
                "category": "Other",
                "supported_query_types": ["search", "info"],
                "rate_limits": "unknown",
                "requires_key": True,
            }),
        }
        for svc in available
    ]
