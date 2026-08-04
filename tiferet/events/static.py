"""Tiferet Static Domain Events"""

# *** imports

# ** app
# Re-export RaiseError from assets.exceptions so consumers can import it from
# either the events or assets layer without circular imports.
from ..assets.exceptions import RaiseError
