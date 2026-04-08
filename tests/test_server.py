from __future__ import annotations

import unittest

from synapse.config import Settings
from synapse.server import app, create_app


class ServerTest(unittest.TestCase):
    def test_routes_exist(self) -> None:
        routes = getattr(app, "routes", [])
        paths = {route.path for route in routes}

        self.assertIn("/health", paths)
        self.assertIn("/ready", paths)
        self.assertIn("/info", paths)

    def test_endpoint_payloads(self) -> None:
        instance = create_app(
            Settings(
                environment="staging",
                deployment_target="staging",
                public_base_url="https://synapse.example.com",
                reverse_proxy="caddy",
                database_url="postgresql+psycopg://synapse:synapse@postgres:5432/synapse",
                redis_url="redis://redis:6379/0",
                minio_endpoint="minio:9000",
                grobid_url="http://grobid:8070",
                llm_provider="openai",
            )
        )
        routes = {route.path: route.endpoint for route in getattr(instance, "routes", [])}

        self.assertEqual(
            routes["/health"](),
            {
                "status": "ok",
                "environment": "staging",
                "deployment_target": "staging",
            },
        )
        ready = routes["/ready"]()
        self.assertEqual(ready["status"], "ok")
        self.assertEqual(ready["reverse_proxy"], "caddy")
        info = routes["/info"]()
        self.assertEqual(info["app_name"], "Synapse")
        self.assertEqual(info["deployment_target"], "staging")
        self.assertIn("docling", info["components"])
        self.assertEqual(info["warnings"], [])

    def test_ready_warns_for_server_localhost_misconfig(self) -> None:
        instance = create_app(
            Settings(
                environment="staging",
                deployment_target="staging",
            )
        )
        routes = {route.path: route.endpoint for route in getattr(instance, "routes", [])}

        ready = routes["/ready"]()

        self.assertEqual(ready["status"], "fail")
        self.assertTrue(ready["warnings"])
        checks = {item["name"]: item for item in ready["checks"]}
        self.assertEqual(checks["database_url"]["status"], "fail")
        self.assertEqual(checks["redis_url"]["status"], "fail")
        self.assertEqual(checks["minio_endpoint"]["status"], "fail")

    def test_ready_warns_when_ingest_concurrency_is_high_on_single_node_vps(self) -> None:
        instance = create_app(
            Settings(
                environment="staging",
                deployment_target="staging",
                public_base_url="https://synapse.example.com",
                reverse_proxy="caddy",
                database_url="postgresql+psycopg://synapse:synapse@postgres:5432/synapse",
                redis_url="redis://redis:6379/0",
                minio_endpoint="minio:9000",
                grobid_url="http://grobid:8070",
                llm_provider="openai",
                ingest_concurrency=4,
            )
        )
        routes = {route.path: route.endpoint for route in getattr(instance, "routes", [])}

        ready = routes["/ready"]()
        checks = {item["name"]: item for item in ready["checks"]}

        self.assertEqual(ready["status"], "warn")
        self.assertEqual(checks["ingest_concurrency"]["status"], "warn")


if __name__ == "__main__":
    unittest.main()
