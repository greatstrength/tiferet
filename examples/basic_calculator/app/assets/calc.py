# *** imports

# ** core
from typing import Dict, Tuple

# *** constants (operators)

# ** constant: add_operator
ADD_OPERATOR = '+'

# ** constant: subtract_operator
SUBTRACT_OPERATOR = '-'

# ** constant: multiply_operator
MULTIPLY_OPERATOR = '*'

# ** constant: divide_operator
DIVIDE_OPERATOR = '/'

# *** constants (groups)

# ** constant: operator_precedence
OPERATOR_PRECEDENCE: Dict[str, int] = {
    ADD_OPERATOR: 1,
    SUBTRACT_OPERATOR: 1,
    MULTIPLY_OPERATOR: 2,
    DIVIDE_OPERATOR: 2,
}

# ** constant: operator_feature_map
OPERATOR_FEATURE_MAP: Dict[str, str] = {
    ADD_OPERATOR: 'calc.add',
    SUBTRACT_OPERATOR: 'calc.subtract',
    MULTIPLY_OPERATOR: 'calc.multiply',
    DIVIDE_OPERATOR: 'calc.divide',
}

# *** constants (cache)

# ** constant: calc_expression_cache_prefix
CALC_EXPRESSION_CACHE_PREFIX: Tuple[str, ...] = (
    'calc',
    'expressions',
)

# *** constants (ids)

# ** constant: no_active_expression_id
NO_ACTIVE_EXPRESSION_ID = 'NO_ACTIVE_EXPRESSION'

# ** constant: expression_already_active_id
EXPRESSION_ALREADY_ACTIVE_ID = 'EXPRESSION_ALREADY_ACTIVE'
