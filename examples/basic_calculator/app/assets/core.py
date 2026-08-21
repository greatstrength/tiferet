# *** imports

# ** core
from typing import Any, Dict, Tuple

# ** infra
from tiferet.assets.core import (
    create_app_service_dependency_data,
    create_service_module_path,
    TIFERET_EVENTS_PATH,
)

# *** constants (paths)

# ** constant: app
APP = 'app'

# ** constant: calc_domain_path
CALC_DOMAIN_PATH = 'calc'

# *** constants (operators)

# ** constant: add_operator
ADD_OPERATOR = '+'

# ** constant: subtract_operator
SUBTRACT_OPERATOR = '-'

# ** constant: multiply_operator
MULTIPLY_OPERATOR = '*'

# ** constant: divide_operator
DIVIDE_OPERATOR = '/'

# ** constant: exponentiate_operator
EXPONENTIATE_OPERATOR = '**'

# ** constant: sqrt_operator
SQRT_OPERATOR = '√'

# *** constants (ids_features)

# ** constant: calc_add_id
CALC_ADD_ID = 'calc.add'

# ** constant: calc_subtract_id
CALC_SUBTRACT_ID = 'calc.subtract'

# ** constant: calc_multiply_id
CALC_MULTIPLY_ID = 'calc.multiply'

# ** constant: calc_divide_id
CALC_DIVIDE_ID = 'calc.divide'

# ** constant: calc_exp_id
CALC_EXP_ID = 'calc.exp'

# ** constant: calc_sqrt_id
CALC_SQRT_ID = 'calc.sqrt'

# ** constant: calc_resolve_id
CALC_RESOLVE_ID = 'calc.resolve'

# *** constants (groups)

# ** constant: operator_precedence
OPERATOR_PRECEDENCE: Dict[str, int] = {
    ADD_OPERATOR: 1,
    SUBTRACT_OPERATOR: 1,
    MULTIPLY_OPERATOR: 2,
    DIVIDE_OPERATOR: 2,
}

# ** constant: operator_feature_map
# Captured once here and reused everywhere else (feature.py's catalog keys,
# this same module's reverse FEATURE_OPERATOR_MAP) instead of being restated
# as literal 'calc.add'-style strings in multiple places.
OPERATOR_FEATURE_MAP: Dict[str, str] = {
    ADD_OPERATOR: CALC_ADD_ID,
    SUBTRACT_OPERATOR: CALC_SUBTRACT_ID,
    MULTIPLY_OPERATOR: CALC_MULTIPLY_ID,
    DIVIDE_OPERATOR: CALC_DIVIDE_ID,
}

# ** constant: feature_operator_map
FEATURE_OPERATOR_MAP: Dict[str, str] = {
    CALC_ADD_ID: ADD_OPERATOR,
    CALC_SUBTRACT_ID: SUBTRACT_OPERATOR,
    CALC_MULTIPLY_ID: MULTIPLY_OPERATOR,
    CALC_DIVIDE_ID: DIVIDE_OPERATOR,
    CALC_EXP_ID: EXPONENTIATE_OPERATOR,
    CALC_SQRT_ID: SQRT_OPERATOR,
}

# *** constants (ids)

# ** constant: no_active_expression_id
NO_ACTIVE_EXPRESSION_ID = 'NO_ACTIVE_EXPRESSION'

# ** constant: expression_already_active_id
EXPRESSION_ALREADY_ACTIVE_ID = 'EXPRESSION_ALREADY_ACTIVE'

# *** constants (ids_services)

# ** constant: add_number_evt_id
ADD_NUMBER_EVT_ID = 'add_number_event'

# ** constant: subtract_number_evt_id
SUBTRACT_NUMBER_EVT_ID = 'subtract_number_event'

# ** constant: multiply_number_evt_id
MULTIPLY_NUMBER_EVT_ID = 'multiply_number_event'

# ** constant: divide_number_evt_id
DIVIDE_NUMBER_EVT_ID = 'divide_number_event'

# ** constant: exponentiate_number_evt_id
EXPONENTIATE_NUMBER_EVT_ID = 'exponentiate_number_event'

# ** constant: resolve_expression_evt_id
RESOLVE_EXPRESSION_EVT_ID = 'resolve_expression_event'

# ** constant: record_run_evt_id
RECORD_RUN_EVT_ID = 'record_run_event'

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

# *** constants (groups_services)

# ** constant: calc_default_services
CALC_DEFAULT_SERVICES: Dict[str, Dict[str, Any]] = {
    ADD_NUMBER_EVT_ID: ADD_NUMBER_EVT_DATA,
    SUBTRACT_NUMBER_EVT_ID: SUBTRACT_NUMBER_EVT_DATA,
    MULTIPLY_NUMBER_EVT_ID: MULTIPLY_NUMBER_EVT_DATA,
    DIVIDE_NUMBER_EVT_ID: DIVIDE_NUMBER_EVT_DATA,
    EXPONENTIATE_NUMBER_EVT_ID: EXPONENTIATE_NUMBER_EVT_DATA,
    RESOLVE_EXPRESSION_EVT_ID: RESOLVE_EXPRESSION_EVT_DATA,
}
