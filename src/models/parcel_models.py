"""Pydantic schemas for Web4AGI REST API.

All request/response bodies are validated here.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


# ── Location ───────────────────────────────────────────────────────────────

class Location(BaseModel):
    lat: float = Field(..., ge=-90, le=90, description="Latitude")
    lng: float = Field(..., ge=-180, le=180, description="Longitude")
    alt: float = Field(0.0, description="Altitude in meters")


# ── Parcel ─────────────────────────────────────────────────────────────────

class ParcelCreate(BaseModel):
    owner_address: str = Field(..., description="Wallet address of the parcel owner")
    location: Location
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("owner_address")
    @classmethod
    def validate_address(cls, v: str) -> str:
        if not v.startswith("0x") or len(v) < 10:
            raise ValueError("owner_address must be a valid 0x wallet address")
        return v.lower()


class ParcelRead(BaseModel):
    parcel_id: str
    owner: str
    location: Location
    balance_usdx: float
    metadata: Dict[str, Any]
    active: bool
    last_updated: str


class ParcelUpdate(BaseModel):
    metadata: Optional[Dict[str, Any]] = None
    active: Optional[bool] = None


# ── Trades ─────────────────────────────────────────────────────────────────

class TradeRequest(BaseModel):
    from_parcel_id: str
    to_parcel_id: str
    amount_usdx: float = Field(..., gt=0, description="Amount in USDx (must be positive)")
    trade_type: str = Field("transfer", description="transfer | lease | data_access")
    contract_terms: Optional[Dict[str, Any]] = None


class TradeResponse(BaseModel):
    success: bool
    tx_id: Optional[str] = None
    amount_usdx: float
    from_parcel_id: str
    to_parcel_id: str
    error: Optional[str] = None


class OfferCreate(BaseModel):
    seller_parcel_id: str
    asset: str = Field(..., description="Asset identifier being sold")
    amount_usdx: float = Field(..., gt=0)
    ttl_seconds: int = Field(300, ge=60, le=86400)


class BidRequest(BaseModel):
    offer_id: str
    bidder_parcel_id: str
    bid_amount_usdx: float = Field(..., gt=0)


# ── Contracts ──────────────────────────────────────────────────────────────

class ContractRequest(BaseModel):
    contract_type: str = Field(..., description="parcel_lease | data_access | custom")
    party_a: str
    party_b: str
    terms: Dict[str, Any]


class ContractResponse(BaseModel):
    contract_id: str
    contract_type: str
    status: str
    parties: Dict[str, str]
    terms: Dict[str, Any]
    created_at: str
    tx_hash: Optional[str] = None


# ── Optimization ────────────────────────────────────────────────────────────

class OptimizeRequest(BaseModel):
    parcel_id: str
    context: Dict[str, Any] = Field(default_factory=dict)


class OptimizeResponse(BaseModel):
    parcel_id: str
    assessment: Optional[str] = None
    strategies: List[str] = []
    chosen_strategy: Optional[str] = None
    actions_taken: List[Dict[str, Any]] = []
    reflection: Optional[str] = None
    score: float = 0.0


# ── Payments ──────────────────────────────────────────────────────────────

class DepositRequest(BaseModel):
    parcel_id: str
    amount_usdx: float = Field(..., gt=0)
    source: str = "stablecoin_bridge"


class PaymentStreamRequest(BaseModel):
    from_parcel_id: str
    to_parcel_id: str
    rate_usdx_per_second: float = Field(..., gt=0)
    duration_seconds: int = Field(..., ge=60)


# ── MCP Messages ───────────────────────────────────────────────────────────

class MCPMessage(BaseModel):
    from_parcel_id: str
    to_parcel_id: str
    msg_type: str = Field(..., description="trade_request | contract_offer | optimize | custom")
    payload: Dict[str, Any]


class MCPToolCall(BaseModel):
    tool_name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)


# ── Generic responses ───────────────────────────────────────────────────────

class SuccessResponse(BaseModel):
    success: bool = True
    message: str = "OK"
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
