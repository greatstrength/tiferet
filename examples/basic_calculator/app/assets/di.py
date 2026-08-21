"""Calculator DI Service Reference Catalog

Default service dependency data for the calculator's arithmetic bounded
context: one *_EVT_DATA constant per arithmetic event, built via the same
create_app_service_dependency_data/create_service_module_path factories
tiferet.assets.core uses for its own defaults, grouped into
CALC_DEFAULT_SERVICES. Service ids themselves stay in core.py (core ->
di, mirroring core -> feature) since app/events/expression.py's
ResolveExpression and app/assets/feature.py's steps reference those same
ids by name; this module only owns the module_path/class_name data those
ids resolve to.
"""

# *** imports

# ** core
from typing import Any, Dict

# ** infra
from tiferet.assets.core import (
    create_app_service_dependency_data,
    create_service_module_path,
    TIFERET_EVENTS_PATH,
)

# ** app
from .core import (
    APP,
    CALC_DOMAIN_PATH,
    ADD_NUMBER_EVT_ID,
    SUBTRACT_NUMBER_EVT_ID,
    MULTIPLY_NUMBER_EVT_ID,
    DIVIDE_NUMBER_EVT_ID,
    EXPONENTIATE_NUMBER_EVT_ID,
    RESOLVE_EXPRESSION_EVT_ID,
)

# *** constants (services)

# ** constant: add_number_evt_data
ADD_NUMBER_EVT_DATA = create_app_service_dependency_data(
    create_service_module_path(APP, TIFERET_EVENTS_PATH, CALC_DOMAIN_PATH),
    'AddNumber',
)

# ** constant: subtract_number_evt_data
SUBTRACT_NUMBER_EVT_DATA = create_app_service_dependency_data(
    create_service_module_path(APP, TIFERET_EVENTS_PATH, CALC_DOMAIN_PATH),
    'SubtractNumber',
)

# ** constant: multiply_number_evt_data
MULTIPLY_NUMBER_EVT_DATA = create_app_service_dependency_data(
    create_service_module_path(APP, TIFERET_EVENTS_PATH, CALC_DOMAIN_PATH),
    'MultiplyNumber',
)

# ** constant: divide_number_evt_data
DIVIDE_NUMBER_EVT_DATA = create_app_service_dependency_data(
    create_service_module_path(APP, TIFERET_EVENTS_PATH, CALC_DOMAIN_PATH),
    'DivideNumber',
)

# ** constant: exponentiate_number_evt_data
EXPONENTIATE_NUMBER_EVT_DATA = create_app_service_dependency_data(
    create_service_module_path(APP, TIFERET_EVENTS_PATH, CALC_DOMAIN_PATH),
    'ExponentiateNumber',
)

# ** constant: resolve_expression_evt_data
RESOLVE_EXPRESSION_EVT_DATA = create_app_service_dependency_data(
    create_service_module_path(APP, TIFERET_EVENTS_PATH, 'expression'),
    'ResolveExpression',
)

# *** constants (groups)

# ** constant: calc_default_services
CALC_DEFAULT_SERVICES: Dict[str, Dict[str, Any]] = {
    ADD_NUMBER_EVT_ID: ADD_NUMBER_EVT_DATA,
    SUBTRACT_NUMBER_EVT_ID: SUBTRACT_NUMBER_EVT_DATA,
    MULTIPLY_NUMBER_EVT_ID: MULTIPLY_NUMBER_EVT_DATA,
    DIVIDE_NUMBER_EVT_ID: DIVIDE_NUMBER_EVT_DATA,
    EXPONENTIATE_NUMBER_EVT_ID: EXPONENTIATE_NUMBER_EVT_DATA,
    RESOLVE_EXPRESSION_EVT_ID: RESOLVE_EXPRESSION_EVT_DATA,
}
