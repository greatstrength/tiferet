"""Calculator Feature Catalog

Default feature workflow definitions for the calculator's arithmetic bounded
context, mirroring tiferet's own assets/feature.py ids -> features -> groups
structure. Each feature carries flags=['app'] so its steps resolve their
arithmetic events from the same cache-seeded 'app'-flagged container that
calc.CALC_DEFAULT_SERVICES populates -- the ordinary per-flag feature DI
system (DIDynamicServiceResolver) reads registrations exclusively from
config.yml's services: block with no cache fallback, so it cannot see these
defaults otherwise.
"""

# *** imports

# ** core
from typing import Any, Dict

# ** infra
from tiferet.assets.core import create_default_feature_data, create_params_schema

# ** app
# Feature and event IDs are captured once in core.py (the calculator's
# foundational assets module, mirroring tiferet's own assets/core.py) and
# imported here rather than restated -- core -> features.
from .core import (
    ADD_NUMBER_EVT_ID,
    SUBTRACT_NUMBER_EVT_ID,
    MULTIPLY_NUMBER_EVT_ID,
    DIVIDE_NUMBER_EVT_ID,
    EXPONENTIATE_NUMBER_EVT_ID,
    CALC_ADD_ID,
    CALC_SUBTRACT_ID,
    CALC_MULTIPLY_ID,
    CALC_DIVIDE_ID,
    CALC_EXP_ID,
    CALC_SQRT_ID,
)

# *** constants (features)

# ** constant: calc_add_data
CALC_ADD_DATA = create_default_feature_data(
    name='Add Number',
    group_id='calc',
    feature_key='add',
    steps=[
        {
            'service_id': ADD_NUMBER_EVT_ID,
            'name': 'Add `a` and `b`',
        },
    ],
    description='Adds one number to another',
    params_schema=create_params_schema(a='float', b='float'),
)

# ** constant: calc_subtract_data
CALC_SUBTRACT_DATA = create_default_feature_data(
    name='Subtract Number',
    group_id='calc',
    feature_key='subtract',
    steps=[
        {
            'service_id': SUBTRACT_NUMBER_EVT_ID,
            'name': 'Subtract `b` from `a`',
        },
    ],
    description='Subtracts one number from another',
    params_schema=create_params_schema(a='float', b='float'),
)

# ** constant: calc_multiply_data
CALC_MULTIPLY_DATA = create_default_feature_data(
    name='Multiply Number',
    group_id='calc',
    feature_key='multiply',
    steps=[
        {
            'service_id': MULTIPLY_NUMBER_EVT_ID,
            'name': 'Multiply `a` and `b`',
        },
    ],
    description='Multiplies one number by another',
    params_schema=create_params_schema(a='float', b='float'),
)

# ** constant: calc_divide_data
CALC_DIVIDE_DATA = create_default_feature_data(
    name='Divide Number',
    group_id='calc',
    feature_key='divide',
    steps=[
        {
            'service_id': DIVIDE_NUMBER_EVT_ID,
            'name': 'Divide `a` by `b`',
        },
    ],
    description='Divides one number by another',
    params_schema=create_params_schema(
        a='float',
        b={
            'type': 'float',
            'description': 'The denominator; must be non-zero.',
        },
    ),
)

# ** constant: calc_exp_data
CALC_EXP_DATA = create_default_feature_data(
    name='Exponentiate Number',
    group_id='calc',
    feature_key='exp',
    steps=[
        {
            'service_id': EXPONENTIATE_NUMBER_EVT_ID,
            'name': 'Raise `a` to the power of `b`',
        },
    ],
    description='Raises one number to the power of another',
)

# ** constant: calc_sqrt_data
CALC_SQRT_DATA = create_default_feature_data(
    name='Square Root',
    group_id='calc',
    feature_key='sqrt',
    steps=[
        {
            'service_id': EXPONENTIATE_NUMBER_EVT_ID,
            'name': 'Calculate square root of `a`',
            'parameters': {'b': '0.5'},
        },
    ],
    description='Calculates the square root of a number',
)

# *** constants (groups)

# ** constant: calc_default_features
# Each default feature carries flags=['app'] -- see module docstring.
CALC_DEFAULT_FEATURES: Dict[str, Dict[str, Any]] = {
    feature_id: {**feature_data, 'flags': ['app']}
    for feature_id, feature_data in {
        CALC_ADD_ID: CALC_ADD_DATA,
        CALC_SUBTRACT_ID: CALC_SUBTRACT_DATA,
        CALC_MULTIPLY_ID: CALC_MULTIPLY_DATA,
        CALC_DIVIDE_ID: CALC_DIVIDE_DATA,
        CALC_EXP_ID: CALC_EXP_DATA,
        CALC_SQRT_ID: CALC_SQRT_DATA,
    }.items()
}
