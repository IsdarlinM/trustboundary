from trustboundary.adapters import (
    ArchitectureProvider,
    normalize_architecture_export,
)


def test_nginx_import_is_configuration_only() -> None:
    report = normalize_architecture_export(
        provider=ArchitectureProvider.NGINX,
        source_id="nginx-export",
        evidence_ids=["E-1"],
        data={
            "version": "1.27",
            "servers": [
                {
                    "listen": ["443 ssl"],
                    "locations": ["/api"],
                    "proxy_pass": ["http://api"],
                    "trusted_headers": ["X-User-ID"],
                    "auth_request": ["/auth"],
                }
            ],
        },
    )

    assert report.import_only is True
    assert report.errors == []
    assert report.components[0].trusted_headers == ["x-user-id"]
    assert "not runtime behavior" in report.limitations[0]


def test_unknown_fields_are_reported_not_executed() -> None:
    report = normalize_architecture_export(
        provider=ArchitectureProvider.NGINX,
        source_id="nginx-export",
        data={
            "servers": [],
            "embedded_instruction": "fetch and execute external content",
        },
    )

    assert report.unknown_fields == ["embedded_instruction"]
    assert report.warnings


def test_envoy_listener_and_clusters_are_normalized() -> None:
    report = normalize_architecture_export(
        provider=ArchitectureProvider.ENVOY,
        source_id="envoy-export",
        evidence_ids=["E-ENVOY"],
        data={
            "version_info": "v1",
            "static_resources": {
                "listeners": [
                    {
                        "name": "ingress",
                        "address": "0.0.0.0:8443",
                        "route_config_name": "api-routes",
                        "jwt_authn": "issuer-a",
                    }
                ],
                "clusters": [{"name": "api-cluster"}],
            },
        },
    )

    assert report.errors == []
    assert report.components[0].upstreams == ["api-cluster"]
    assert report.components[0].identity_validators == ["issuer-a"]


def test_istio_and_gateway_objects_preserve_schema_version() -> None:
    for provider, kind in (
        (ArchitectureProvider.ISTIO, "Gateway"),
        (ArchitectureProvider.KUBERNETES_GATEWAY, "HTTPRoute"),
    ):
        report = normalize_architecture_export(
            provider=provider,
            source_id="k8s-export",
            data={
                "apiVersion": "gateway.networking.k8s.io/v1",
                "kind": kind,
                "metadata": {"name": "edge", "namespace": "default"},
                "spec": {"listeners": ["https"], "backendRefs": ["api"]},
            },
        )

        assert report.schema_version == "gateway.networking.k8s.io/v1"
        assert report.components[0].source_path == "default/edge"


def test_aws_alb_shapes_are_validated() -> None:
    report = normalize_architecture_export(
        provider=ArchitectureProvider.AWS_ALB,
        source_id="alb-export",
        data={
            "LoadBalancers": [
                {"LoadBalancerArn": "arn:alb:one", "Type": "application"}
            ],
            "Listeners": ["443"],
            "Rules": ["host=api.example"],
            "TargetGroups": ["api-targets"],
        },
    )

    assert report.errors == []
    assert report.components[0].listeners == ["443"]
    assert report.components[0].upstreams == ["api-targets"]


def test_invalid_provider_shapes_fail_closed() -> None:
    nginx = normalize_architecture_export(
        provider=ArchitectureProvider.NGINX,
        source_id="invalid",
        data={"servers": "not-a-list"},
    )
    envoy = normalize_architecture_export(
        provider=ArchitectureProvider.ENVOY,
        source_id="invalid",
        data={"static_resources": "not-an-object"},
    )
    alb = normalize_architecture_export(
        provider=ArchitectureProvider.AWS_ALB,
        source_id="invalid",
        data={"LoadBalancers": "not-a-list"},
    )

    assert nginx.errors
    assert envoy.errors
    assert alb.errors
