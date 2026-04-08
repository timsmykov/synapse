from __future__ import annotations

import unittest

import synapse.cli as cli

try:
    from typer.testing import CliRunner
except ModuleNotFoundError:
    CliRunner = None


class CliTest(unittest.TestCase):
    def test_commands_are_registered(self) -> None:
        if hasattr(cli.app, "registered_commands"):
            commands = {command.name for command in cli.app.registered_commands}
        else:
            commands = set(getattr(cli.app, "commands", {}))

        self.assertIn("ingest", commands)
        self.assertIn("query", commands)
        self.assertIn("analyze", commands)
        self.assertIn("doctor", commands)

    def test_command_payloads_are_serializable(self) -> None:
        self.assertEqual(
            cli.ingest(),
            {"command": "ingest", "source": "test_corpus", "output": "data/corpus.db"},
        )
        self.assertEqual(
            cli.query(prompt="find table"),
            {"command": "query", "prompt": "find table", "limit": 5},
        )
        self.assertEqual(
            cli.analyze(),
            {"command": "analyze", "corpus": "data/corpus.db", "mode": "systematic-review"},
        )

    @unittest.skipIf(CliRunner is None, "Typer is not installed")
    def test_help_renders(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli.app, ["--help"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("Synapse CLI", result.stdout)


if __name__ == "__main__":
    unittest.main()
