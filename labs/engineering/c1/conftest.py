"""Make the lab modules (llm, tokens, decomposition, variance) importable from the tests.

Every lab has its own ``llm.py``. When pytest runs several labs in one process, a module
imported by an earlier lab would be reused here, so we drop any cached module that shares a
name with a file in this folder but was loaded from somewhere else.
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _py in HERE.glob("*.py"):
    _cached = None if _py.stem == "conftest" else sys.modules.get(_py.stem)
    if _cached is not None and Path(getattr(_cached, "__file__", "") or "").resolve().parent != HERE:
        del sys.modules[_py.stem]
if str(HERE) in sys.path:
    sys.path.remove(str(HERE))
sys.path.insert(0, str(HERE))
