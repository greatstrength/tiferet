"""Tiferet App Blueprint — Default Built-in Application Interface

-- obsolete: superseded by blueprints/admin.py; remove at v2.0.0 stable
"""

# *** imports

# ** app
from .admin import build_admin_app

# *** blueprints

# ** blueprint: build_tiferet_app (obsolete)
# -- obsolete: superseded by admin.build_admin_app; remove at v2.0.0 stable
build_tiferet_app = build_admin_app
