"""Make the lab modules (llm, app) importable from the tests."""
import sys
from pathlib import Path

HERE = str(Path(__file__).resolve().parent)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
