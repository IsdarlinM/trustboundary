from __future__ import annotations
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from sric.models import ClaimStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class NodeType(StrEnum):
    ZONE = "ZONE"
    SERVICE = "SERVICE"
    PROXY = "PROXY"
    GATEWAY = "GATEWAY"
    IDENTITY = "IDENTITY"
    CREDENTIAL = "CREDENTIAL"
    NETWORK = "NETWORK"


class Node(BaseModel):
    model_config = ConfigDict(extra="forbid")
    node_id: str
    name: str
    node_type: NodeType
    public_reachable: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class Transition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    transition_id: str
    source_node_id: str
    target_node_id: str
    data_type: str
    input_name: str | None = None
    output_name: str | None = None
    transformation: str | None = None
    verified: bool | None = None
    evidence_ids: list[str] = Field(default_factory=list)
    observed_at: datetime = Field(default_factory=utcnow)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TrustAssertion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    assertion_id: str
    node_id: str
    statement: str
    basis: str
    evidence_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AssumptionCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    candidate_id: str
    title: str
    status: ClaimStatus = ClaimStatus.HYPOTHESIS
    confidence: float = Field(ge=0, le=1)
    node_ids: list[str]
    evidence_ids: list[str] = Field(default_factory=list)
    counter_evidence: list[str] = Field(default_factory=list)
    reasoning: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
