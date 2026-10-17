"""Verificar as entradas públicas do pacote a partir de processos reais."""

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class EntrypointTests(unittest.TestCase):
    def run_help(self, arguments, cwd):
        result = subprocess.run(
            [sys.executable] + arguments + ["--help"], cwd=str(cwd),
            capture_output=True, text=True, encoding="utf-8", timeout=10,
            env=dict(os.environ, PYTHONIOENCODING="utf-8"),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage: guara", result.stdout)
        self.assertIn("--texto", result.stdout)

    def test_package_entrypoint(self):
        self.run_help(["-m", "guara"], Path(__file__).resolve().parents[1])

    def test_global_launcher_entrypoint_from_another_directory(self):
        script = Path(__file__).resolve().parents[1] / "scripts" / "iniciar_guara.py"
        self.run_help([str(script)], tempfile.gettempdir())


if __name__ == "__main__":
    unittest.main()
