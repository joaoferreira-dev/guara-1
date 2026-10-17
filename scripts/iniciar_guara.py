"""Ponto de entrada do comando global, independente da pasta atual."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from guara.cli import launch


if __name__ == "__main__":
    launch()
