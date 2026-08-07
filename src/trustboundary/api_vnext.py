from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import APIRouter, FastAPI
from pydantic import BaseModel, ConfigDict, Field

from .adapters import ArchitectureProvider, normalize_architecture_export
from .api import create_app as create_base_app
from .layers import TrustLayerObservation, analyze_forwarding_headers, compare_trust_layers
from .provenance import IdentityProvenanceStep, analyze_identity_provenance
from .websocket import WebSocketTrustObservation, analyze_websocket_trust_paths


class TrustLayerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    observations: list[TrustLayerObservation]


class HeaderRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    headers: list[tuple[str, str]]


class ArchitectureImportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    provider: ArchitectureProvider
    source_id: str
    data: dict[str, Any]
    evidence_ids: list[str] = Field(default_factory=list)


class ProvenanceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    steps: list[IdentityProvenanceStep]


class WebSocketTrustRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    observations: list[WebSocketTrustObservation]


router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])


@router.post("/layers/compare")
async def layer_compare(request: TrustLayerRequest) -> dict[str, object]:
    comparisons = compare_trust_layers(request.observations)
    return {
        "comparisons": [item.model_dump(mode="json") for item in comparisons],
        "exploitability_established": False,
        "validated_findings_created": 0,
    }


@router.post("/headers/analyze")
async def header_analysis(request: HeaderRequest) -> dict[str, object]:
    report = analyze_forwarding_headers(request.headers)
    return {"analysis": report.model_dump(mode="json"), "trusted_identity_selected": False}


@router.post("/architecture/import")
async def architecture_import(request: ArchitectureImportRequest) -> dict[str, object]:
    report = normalize_architecture_export(
        provider=request.provider,
        source_id=request.source_id,
        data=request.data,
        evidence_ids=request.evidence_ids,
    )
    return {"report": report.model_dump(mode="json"), "executed": False, "runtime_behavior_proved": False}


@router.post("/provenance/analyze")
async def provenance_analysis(request: ProvenanceRequest) -> dict[str, object]:
    reports = analyze_identity_provenance(request.steps)
    return {
        "reports": [item.model_dump(mode="json") for item in reports],
        "authorization_correctness_proved": False,
        "exploitability_established": False,
    }


@router.post("/websocket/trust-paths")
async def websocket_trust_paths(request: WebSocketTrustRequest) -> dict[str, object]:
    reports = analyze_websocket_trust_paths(request.observations)
    return {
        "reports": [item.model_dump(mode="json") for item in reports],
        "exploitability_established": False,
        "validated_findings_created": 0,
    }


def create_app(workspace: Path) -> FastAPI:
    app = create_base_app(workspace)
    app.include_router(router)
    return app
