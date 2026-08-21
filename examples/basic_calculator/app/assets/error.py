"""Calculator Error Catalog

Default error definitions for the calculator's arithmetic bounded context,
mirroring tiferet's own assets/error.py ids -> models -> groups structure.
Both errors are raised directly by the default arithmetic events
(BasicCalcEvent.verify_number and DivideNumber.execute), so they ship as
defaults alongside the operators themselves, regardless of config.yml.
"""

# *** imports

# ** infra
from tiferet.assets.core import EN_US, create_default_error_data

# *** constants (ids)

# ** constant: invalid_input_id
INVALID_INPUT_ID = 'INVALID_INPUT'

# ** constant: division_by_zero_id
DIVISION_BY_ZERO_ID = 'DIVISION_BY_ZERO'

# *** constants (models)

# ** constant: invalid_input_data
INVALID_INPUT_DATA = create_default_error_data(
    'Invalid Numeric Input',
    [
        (EN_US, 'Value {value} must be a number'),
        ('es_ES', 'El valor {value} debe ser un número'),
    ],
)

# ** constant: division_by_zero_data
DIVISION_BY_ZERO_DATA = create_default_error_data(
    'Division By Zero',
    [
        (EN_US, 'Cannot divide by zero'),
        ('es_ES', 'No se puede dividir por cero'),
    ],
)

# *** constants (groups)

# ** constant: calc_default_errors
CALC_DEFAULT_ERRORS = {
    INVALID_INPUT_ID: INVALID_INPUT_DATA,
    DIVISION_BY_ZERO_ID: DIVISION_BY_ZERO_DATA,
}
