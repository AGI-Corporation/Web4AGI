"""Integration tests for Web4AGI API v1."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_root_endpoint(client):
    """Test the root API endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "Web4AGI"


def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_parcel_lifecycle(client):
    """Test creating, getting, and updating a parcel agent via API."""
    # 1. Create
    parcel_data = {
        "owner_address": "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        "location": {"lat": 37.7749, "lng": -122.4194},
        "metadata": {"type": "residential"},
    }
    response = client.post("/api/v1/parcels/", json=parcel_data)
    assert response.status_code == 201
    parcel = response.json()
    parcel_id = parcel["parcel_id"]
    assert parcel["owner"] == parcel_data["owner_address"].lower()

    # 2. Get
    response = client.get(f"/api/v1/parcels/{parcel_id}")
    assert response.status_code == 200
    assert response.json()["metadata"]["type"] == "residential"

    # 3. Update
    update_data = {"metadata": {"zone": "sf-mission"}, "active": False}
    response = client.patch(f"/api/v1/parcels/{parcel_id}", json=update_data)
    assert response.status_code == 200
    updated = response.json()
    assert updated["metadata"]["zone"] == "sf-mission"
    assert updated["active"] is False

    # 4. Delete
    response = client.delete(f"/api/v1/parcels/{parcel_id}")
    assert response.status_code == 200


def test_trade_flow(client):
    """Test creating an offer and placing a bid via API."""
    # Setup: create two parcels
    p1 = client.post(
        "/api/v1/parcels/",
        json={
            "owner_address": "0x1111111111111111111111111111111111111111",
            "location": {"lat": 0, "lng": 0},
        },
    ).json()
    p2 = client.post(
        "/api/v1/parcels/",
        json={
            "owner_address": "0x2222222222222222222222222222222222222222",
            "location": {"lat": 1, "lng": 1},
        },
    ).json()

    # 1. Create Offer
    offer_data = {
        "seller_parcel_id": p1["parcel_id"],
        "asset": "data_lease_001",
        "amount_usdx": 100.0,
    }
    response = client.post("/api/v1/trades/offers", json=offer_data)
    assert response.status_code == 201
    offer = response.json()
    offer_id = offer["offer_id"]

    # 2. Place Bid
    bid_data = {
        "offer_id": offer_id,
        "bidder_parcel_id": p2["parcel_id"],
        "bid_amount_usdx": 110.0,
    }
    response = client.post("/api/v1/trades/bids", json=bid_data)
    assert response.status_code == 200
    assert response.json()["success"] is True

    # 3. Close Offer
    response = client.post(f"/api/v1/trades/close/{offer_id}")
    assert response.status_code == 200
    result = response.json()
    assert result["winner"] == p2["parcel_id"]
    assert result["amount"] == 110.0


def test_mcp_discovery(client):
    """Test listing MCP tools via API."""
    response = client.get("/api/v1/mcp/tools")
    assert response.status_code == 200
    tools = response.json()["tools"]
    assert len(tools) > 0
    # Check for a known tool stub
    tool_names = [t["name"] for t in tools]
    assert "parcel_get_place_hierarchy" in tool_names


def test_system_visibility(client):
    """Test OS-level system visibility endpoints."""
    # 1. Status
    response = client.get("/api/v1/system/status")
    assert response.status_code == 200
    data = response.json()
    assert "agents_online" in data
    assert "subsystems" in data

    # 2. Map
    response = client.get("/api/v1/system/map")
    assert response.status_code == 200
    geojson = response.json()
    assert geojson["type"] == "FeatureCollection"
