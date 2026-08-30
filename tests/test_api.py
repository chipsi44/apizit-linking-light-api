import ast
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import httpx
from apizit_linking import compile_linking_file
from apizit_linking.fastapi import create_app

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_manifest_declares_exact_route_contract():
    result = compile_linking_file(PROJECT_ROOT / "apizit_linking.yaml", PROJECT_ROOT)

    assert result.is_valid, [diagnostic.to_dict() for diagnostic in result.diagnostics]
    assert {(route.definition.method, route.definition.path) for route in result.routes} == {
        ("GET", "/health"),
        ("GET", "/info"),
        ("POST", "/echo"),
        ("GET", "/items/{item_id}"),
        ("GET", "/slow"),
    }


def test_business_code_has_no_web_or_linking_imports():
    tree = ast.parse((PROJECT_ROOT / "service.py").read_text(encoding="utf-8"))
    imported_roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.partition(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            imported_roots.add(node.module.partition(".")[0])

    assert not imported_roots & {"apizit_linking", "fastapi", "flask", "mangum"}


def client(application=None, *, raise_app_exceptions=True):
    application = application or create_app(PROJECT_ROOT)
    transport = httpx.ASGITransport(
        app=application,
        raise_app_exceptions=raise_app_exceptions,
    )
    return httpx.AsyncClient(transport=transport, base_url="http://example.test")


def linked_globals(application) -> dict[str, object]:
    route = next(route for route in application.routes if route.path == "/health")
    linked_function = route.endpoint.__closure__[0].cell_contents
    return linked_function.__globals__


class TestHttpContract(unittest.IsolatedAsyncioTestCase):
    async def test_health_is_immediate(self):
        async with client() as api_client:
            response = await api_client.get("/health")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    async def test_info(self):
        async with client() as api_client:
            response = await api_client.get("/info")

        assert response.status_code == 200
        assert response.json() == {"framework": "linking", "profile": "light"}

    async def test_echo_round_trip_and_validation(self):
        async with client() as api_client:
            response = await api_client.post(
                "/echo",
                json={"message": "hello", "count": 2},
            )
            invalid = await api_client.post(
                "/echo",
                json={"message": "hello", "count": "two"},
            )

        assert response.status_code == 200
        assert response.json() == {"received": {"message": "hello", "count": 2}}
        assert invalid.status_code == 400

    async def test_item_path_and_query_parameters(self):
        async with client() as api_client:
            response = await api_client.get(
                "/items/7",
                params={"include_details": "true"},
            )

        assert response.status_code == 200
        assert response.json() == {
            "details": "Reference item 7",
            "include_details": True,
            "item_id": 7,
        }

    async def test_slow_uses_exact_duration_without_waiting(self):
        application = create_app(PROJECT_ROOT)
        mocked_sleep = Mock()
        with patch.dict(linked_globals(application), {"sleep": mocked_sleep}):
            async with client(application) as api_client:
                response = await api_client.get("/slow")

        assert response.status_code == 200
        mocked_sleep.assert_called_once_with(80)
        assert response.json() == {"delay_seconds": 80, "status": "completed"}
