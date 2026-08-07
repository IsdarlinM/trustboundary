"""TrustBoundary Mapper."""

from .adapters import (
    ArchitectureImportReport,
    ArchitectureProvider,
    ImportedComponent,
    normalize_architecture_export,
)
from .layers import (
    ArchitectureLayer,
    HeaderAnalysis,
    TrustDrift,
    TrustLayerComparison,
    TrustLayerObservation,
    analyze_forwarding_headers,
    compare_trust_layers,
)
from .provenance import (
    IdentityArtifactType,
    IdentityProvenanceReport,
    IdentityProvenanceStep,
    ProvenanceStepType,
    analyze_identity_provenance,
)
from .websocket import (
    WebSocketTrustObservation,
    WebSocketTrustPath,
    WebSocketTrustStage,
    analyze_websocket_trust_paths,
)

__all__ = [
    "ArchitectureImportReport",
    "ArchitectureLayer",
    "ArchitectureProvider",
    "HeaderAnalysis",
    "IdentityArtifactType",
    "IdentityProvenanceReport",
    "IdentityProvenanceStep",
    "ImportedComponent",
    "ProvenanceStepType",
    "TrustDrift",
    "TrustLayerComparison",
    "TrustLayerObservation",
    "WebSocketTrustObservation",
    "WebSocketTrustPath",
    "WebSocketTrustStage",
    "analyze_forwarding_headers",
    "analyze_identity_provenance",
    "analyze_websocket_trust_paths",
    "compare_trust_layers",
    "normalize_architecture_export",
]
__version__ = "0.3.1"
