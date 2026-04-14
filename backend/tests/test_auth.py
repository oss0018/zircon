"""Basic auth tests."""

import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_register_success(client: AsyncClient):
    """Test successful user registration."""
    response = await client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "username": "testuser", "password": "testpassword123"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_register_duplicate_email(client: AsyncClient):
    """Test registration with duplicate email."""
    payload = {"email": "dup@example.com", "username": "user1", "password": "pass123"}
    await client.post("/api/v1/auth/register", json=payload)

    payload2 = {"email": "dup@example.com", "username": "user2", "password": "pass123"}
    response = await client.post("/api/v1/auth/register", json=payload2)
    assert response.status_code == 400


async def test_login_success(client: AsyncClient):
    """Test successful login."""
    # Register first
    await client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "username": "loginuser", "password": "testpass"},
    )
    # Login
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "login@example.com", "password": "testpass"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


async def test_login_invalid_credentials(client: AsyncClient):
    """Test login with invalid credentials."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


async def test_get_me_authenticated(client: AsyncClient):
    """Test /me endpoint with authentication."""
    reg_response = await client.post(
        "/api/v1/auth/register",
        json={"email": "me@example.com", "username": "meuser", "password": "mepass"},
    )
    token = reg_response.json()["access_token"]

    response = await client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "me@example.com"
    assert data["username"] == "meuser"


async def test_get_me_unauthenticated(client: AsyncClient):
    """Test /me endpoint without authentication."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 403
