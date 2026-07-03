"""Pytest configuration for the basic calculator example tests."""

# *** imports

# ** core
import sys
from pathlib import Path

# *** setup

# Add the example root to sys.path so the `app` package is importable
# regardless of the directory pytest is invoked from.
EXAMPLE_ROOT = Path(__file__).resolve().parent.parent
if str(EXAMPLE_ROOT) not in sys.path:
    sys.path.insert(0, str(EXAMPLE_ROOT))
