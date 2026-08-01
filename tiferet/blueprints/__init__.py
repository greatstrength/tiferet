"""Tiferet Blueprint Exports"""

# *** exports

# ** app
# ++ todo: main.py is pending retirement by ST4 Child 5 (#914) and is already broken
# (dangling AppInterfaceContext/a.core references from ST4 Child 1 #911). Guard the
# import, mirroring the top-level tiferet/__init__.py pattern, so submodules such as
# tiferet.blueprints.core remain directly importable in the interim.
try:
    from .main import build_app, build_app as App
    from .cli import build_app as build_cli, build_app as CLI
except Exception as e:
    import os, sys
    if not os.getenv('TIFERET_SILENT_IMPORTS'):
        print(f"Warning: Failed to import Tiferet blueprint modules: {e}", file=sys.stderr)
