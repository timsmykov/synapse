from __future__ import annotations

import unittest

from synapse.server import app, create_app


class ServerTest(unittest.TestCase):
    def test_routes_exist(self) -> None:
        routes = getattr(app, "routes", [])
        paths = {route.path for route in routes}

        self.assertIn("/health", paths)
        self.assertIn("/info", paths)

    def test_endpoint_payloads(self) -> None:
        instance = create_app()
        routes = {route.path: route.endpoint for route in getattr(instance, "routes", [])}

        self.assertEqual(routes["/health"](), {"status": "ok"})
        info = routes["/info"]()
        self.assertEqual(info["app_name"], "Synapse")
        self.assertIn("docling", info["components"])


if __name__ == "__main__":
    unittest.main()
