"""Tests for the integration registry and service-metadata endpoint.

Verifies that:
  - CTX.io and CheckPhish are present in the registry.
  - The GET /api/v1/integrations/services endpoint lists both services.
  - Both connectors can be instantiated and expose the required interface.

Note: The /services endpoint returns the human-readable display name
(e.g. "CTX.io", "CheckPhish") in the ``name`` field, not the registry key.
"""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Registry unit tests (no HTTP, not async)
# ---------------------------------------------------------------------------

def test_registry_contains_ctxio():
    """CTXioIntegration must be registered under 'ctxio'."""
    from app.integrations import IntegrationRegistry
    assert "ctxio" in IntegrationRegistry.list_available()


def test_registry_contains_checkphish():
    """CheckPhishIntegration must be registered under 'checkphish'."""
    from app.integrations import IntegrationRegistry
    assert "checkphish" in IntegrationRegistry.list_available()


def test_ctxio_instance_interface():
    """CTXioIntegration must expose search and get_info callables."""
    from app.integrations import IntegrationRegistry
    instance = IntegrationRegistry.create_instance("ctxio", api_key="test-key")
    assert callable(getattr(instance, "search", None))
    assert callable(getattr(instance, "get_info", None))


def test_checkphish_instance_interface():
    """CheckPhishIntegration must expose search and get_info callables."""
    from app.integrations import IntegrationRegistry
    instance = IntegrationRegistry.create_instance("checkphish", api_key="test-key")
    assert callable(getattr(instance, "search", None))
    assert callable(getattr(instance, "get_info", None))


# ---------------------------------------------------------------------------
# Service-metadata endpoint tests (require the HTTP client fixture)
# ---------------------------------------------------------------------------

async def test_services_endpoint_includes_ctxio(client: AsyncClient):
    """GET /api/v1/integrations/services must include CTX.io."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "svc_ctxio@example.com", "username": "svc_ctxio", "password": "pass1234"},
    )
    assert reg.status_code == 201, reg.text
    token = reg.json()["access_token"]

    resp = await client.get(
        "/api/v1/integrations/services",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    names = [s["name"] for s in resp.json()]
    assert "CTX.io" in names, f"CTX.io not found in: {names}"


async def test_services_endpoint_includes_checkphish(client: AsyncClient):
    """GET /api/v1/integrations/services must include CheckPhish."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "svc_cp@example.com", "username": "svc_cp", "password": "pass1234"},
    )
    assert reg.status_code == 201, reg.text
    token = reg.json()["access_token"]

    resp = await client.get(
        "/api/v1/integrations/services",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200, resp.text
    names = [s["name"] for s in resp.json()]
    assert "CheckPhish" in names, f"CheckPhish not found in: {names}"


async def test_services_endpoint_ctxio_metadata(client: AsyncClient):
    """CTX.io service entry must carry expected metadata fields."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "meta_ctx@example.com", "username": "meta_ctx", "password": "pass1234"},
    )
    token = reg.json()["access_token"]

    resp = await client.get(
        "/api/v1/integrations/services",
        headers={"Authorization": f"Bearer {token}"},
    )
    services = {s["name"]: s for s in resp.json()}
    assert "CTX.io" in services
    svc = services["CTX.io"]
    assert svc.get("category") == "Phishing & Malware"
    assert svc.get("requires_key") is True
    assert "search" in svc.get("supported_query_types", [])


async def test_services_endpoint_checkphish_metadata(client: AsyncClient):
    """CheckPhish service entry must carry expected metadata fields."""
    reg = await client.post(
        "/api/v1/auth/register",
        json={"email": "meta_cp@example.com", "username": "meta_cp", "password": "pass1234"},
    )
    token = reg.json()["access_token"]

    resp = await client.get(
        "/api/v1/integrations/services",
        headers={"Authorization": f"Bearer {token}"},
    )
    services = {s["name"]: s for s in resp.json()}
    assert "CheckPhish" in services
    svc = services["CheckPhish"]
    assert svc.get("category") == "Phishing & Malware"
    assert svc.get("requires_key") is True
    assert "scan" in svc.get("supported_query_types", [])
