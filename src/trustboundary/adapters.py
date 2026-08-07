from __future__ import annotations

import hashlib
import json
from enum import StrEnum
from typing import Any, Iterable

from pydantic import BaseModel, ConfigDict, Field


class ArchitectureProvider(StrEnum):
    NGINX = "NGINX"
    ENVOY = "ENVOY"
    ISTIO = "ISTIO"
    KUBERNETES_GATEWAY = "KUBERNETES_GATEWAY"
    AWS_ALB = "AWS_ALB"


class ImportedComponent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    component_id: str
    component_type: str
    provider: ArchitectureProvider
    source_path: str
    listeners: list[str] = Field(default_factory=list)
    routes: list[str] = Field(default_factory=list)
    upstreams: list[str] = Field(default_factory=list)
    trusted_headers: list[str] = Field(default_factory=list)
    identity_validators: list[str] = Field(default_factory=list)
    evidence_ids: list[str] = Field(default_factory=list)


class ArchitectureImportReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    provider: ArchitectureProvider
    source_id: str
    content_sha256: str
    import_only: bool = True
    schema_version: str | None = None
    components: list[ImportedComponent] = Field(default_factory=list)
    unknown_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


def _hash(value: dict[str, Any]) -> str:
    canonical = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _strings(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _component_id(provider: ArchitectureProvider, source_path: str) -> str:
    digest = hashlib.sha256(f"{provider.value}\x00{source_path}".encode()).hexdigest()
    return f"{provider.value}-{digest[:12]}"


def _nginx(
    data: dict[str, Any], evidence_ids: list[str]
) -> tuple[list[ImportedComponent], list[str], list[str], str | None]:
    allowed = {"version", "servers", "upstreams", "http", "stream"}
    unknown = sorted(set(data) - allowed)
    errors: list[str] = []
    servers = data.get("servers", [])
    if not isinstance(servers, list):
        return [], unknown, ["NGINX servers must be a list"], str(data.get("version") or "")
    components: list[ImportedComponent] = []
    for index, server in enumerate(servers):
        if not isinstance(server, dict):
            errors.append(f"servers[{index}] is not an object")
            continue
        path = f"servers[{index}]"
        components.append(
            ImportedComponent(
                component_id=_component_id(ArchitectureProvider.NGINX, path),
                component_type="reverse_proxy",
                provider=ArchitectureProvider.NGINX,
                source_path=path,
                listeners=_strings(server.get("listen")),
                routes=_strings(server.get("locations")),
                upstreams=_strings(server.get("proxy_pass")),
                trusted_headers=[
                    str(item).lower()
                    for item in _strings(server.get("trusted_headers"))
                ],
                identity_validators=_strings(server.get("auth_request")),
                evidence_ids=evidence_ids,
            )
        )
    return components, unknown, errors, str(data.get("version") or "") or None


def _envoy(
    data: dict[str, Any], evidence_ids: list[str]
) -> tuple[list[ImportedComponent], list[str], list[str], str | None]:
    allowed = {"@type", "version_info", "static_resources", "dynamic_resources", "admin"}
    unknown = sorted(set(data) - allowed)
    resources = data.get("static_resources", {})
    if not isinstance(resources, dict):
        return [], unknown, ["Envoy static_resources must be an object"], None
    listeners = resources.get("listeners", [])
    clusters = resources.get("clusters", [])
    if not isinstance(listeners, list):
        listeners = []
    if not isinstance(clusters, list):
        clusters = []
    cluster_names = [
        str(item.get("name"))
        for item in clusters
        if isinstance(item, dict) and item.get("name")
    ]
    components: list[ImportedComponent] = []
    errors: list[str] = []
    for index, listener in enumerate(listeners):
        if not isinstance(listener, dict):
            errors.append(f"static_resources.listeners[{index}] is not an object")
            continue
        path = f"static_resources.listeners[{index}]"
        components.append(
            ImportedComponent(
                component_id=_component_id(ArchitectureProvider.ENVOY, path),
                component_type="proxy_listener",
                provider=ArchitectureProvider.ENVOY,
                source_path=path,
                listeners=_strings(listener.get("address")),
                routes=_strings(listener.get("route_config_name")),
                upstreams=cluster_names,
                trusted_headers=[
                    str(item).lower()
                    for item in _strings(listener.get("trusted_headers"))
                ],
                identity_validators=_strings(listener.get("jwt_authn")),
                evidence_ids=evidence_ids,
            )
        )
    version = str(data.get("version_info") or "") or None
    return components, unknown, errors, version


def _kubernetes_like(
    provider: ArchitectureProvider,
    data: dict[str, Any],
    evidence_ids: list[str],
) -> tuple[list[ImportedComponent], list[str], list[str], str | None]:
    allowed = {"apiVersion", "kind", "metadata", "spec", "status"}
    unknown = sorted(set(data) - allowed)
    metadata = data.get("metadata", {})
    spec = data.get("spec", {})
    if not isinstance(metadata, dict):
        metadata = {}
    if not isinstance(spec, dict):
        return [], unknown, ["spec must be an object"], str(data.get("apiVersion") or "")
    name = str(metadata.get("name") or "unnamed")
    namespace = str(metadata.get("namespace") or "default")
    path = f"{namespace}/{name}"
    listeners = _strings(spec.get("listeners") or spec.get("hosts"))
    routes = _strings(spec.get("http") or spec.get("rules"))
    upstreams = _strings(
        spec.get("backendRefs")
        or spec.get("backend")
        or spec.get("route")
        or spec.get("selector")
    )
    validators = _strings(
        spec.get("jwtRules")
        or spec.get("provider")
        or spec.get("targetRefs")
    )
    component = ImportedComponent(
        component_id=_component_id(provider, path),
        component_type=str(data.get("kind") or "gateway_resource"),
        provider=provider,
        source_path=path,
        listeners=listeners,
        routes=routes,
        upstreams=upstreams,
        identity_validators=validators,
        evidence_ids=evidence_ids,
    )
    return [component], unknown, [], str(data.get("apiVersion") or "") or None


def _aws_alb(
    data: dict[str, Any], evidence_ids: list[str]
) -> tuple[list[ImportedComponent], list[str], list[str], str | None]:
    allowed = {"LoadBalancers", "Listeners", "Rules", "TargetGroups", "version"}
    unknown = sorted(set(data) - allowed)
    load_balancers = data.get("LoadBalancers", [])
    if not isinstance(load_balancers, list):
        return [], unknown, ["AWS ALB LoadBalancers must be a list"], None
    components: list[ImportedComponent] = []
    errors: list[str] = []
    listeners = data.get("Listeners", [])
    rules = data.get("Rules", [])
    targets = data.get("TargetGroups", [])
    listener_values = _strings(listeners)
    rule_values = _strings(rules)
    target_values = _strings(targets)
    for index, item in enumerate(load_balancers):
        if not isinstance(item, dict):
            errors.append(f"LoadBalancers[{index}] is not an object")
            continue
        arn = str(item.get("LoadBalancerArn") or f"load-balancer-{index}")
        path = f"LoadBalancers[{index}]"
        components.append(
            ImportedComponent(
                component_id=_component_id(ArchitectureProvider.AWS_ALB, arn),
                component_type=str(item.get("Type") or "application_load_balancer"),
                provider=ArchitectureProvider.AWS_ALB,
                source_path=path,
                listeners=listener_values,
                routes=rule_values,
                upstreams=target_values,
                evidence_ids=evidence_ids,
            )
        )
    return components, unknown, errors, str(data.get("version") or "") or None


def normalize_architecture_export(
    *,
    provider: ArchitectureProvider,
    source_id: str,
    data: dict[str, Any],
    evidence_ids: Iterable[str] = (),
) -> ArchitectureImportReport:
    evidence = sorted(set(evidence_ids))
    if provider is ArchitectureProvider.NGINX:
        components, unknown, errors, version = _nginx(data, evidence)
    elif provider is ArchitectureProvider.ENVOY:
        components, unknown, errors, version = _envoy(data, evidence)
    elif provider in {
        ArchitectureProvider.ISTIO,
        ArchitectureProvider.KUBERNETES_GATEWAY,
    }:
        components, unknown, errors, version = _kubernetes_like(
            provider, data, evidence
        )
    else:
        components, unknown, errors, version = _aws_alb(data, evidence)

    warnings: list[str] = []
    if unknown:
        warnings.append(
            "Unknown top-level fields were retained in the report and not silently interpreted."
        )
    if not evidence:
        warnings.append("No evidence IDs were attached to the imported architecture.")
    return ArchitectureImportReport(
        provider=provider,
        source_id=source_id,
        content_sha256=_hash(data),
        schema_version=version,
        components=components,
        unknown_fields=unknown,
        warnings=warnings,
        errors=errors,
        limitations=[
            "Imported configuration describes a declared or configured architecture layer, not runtime behavior.",
            "Unknown provider fields and unsupported nested semantics remain UNKNOWN.",
            "The importer never executes embedded commands, templates or external references.",
        ],
    )
