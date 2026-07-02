"""Tiferet Basic Calculator Request Schema Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet import TiferetError
from tiferet.domain.feature import RequestSpecification

# *** tests

# ** test: schema_validates_and_coerces
def test_schema_validates_and_coerces():
    '''
    A request schema coerces declared parameters and preserves extras.
    '''

    # Build a schema mirroring the formula.save feature.
    schema = RequestSpecification.model_validate({'name': 'str', 'expression': 'str'})

    # Validation returns the coerced data, preserving unspecified keys.
    validated = schema.validate({'name': 'Rect', 'expression': 'a * b', 'extra': 1})
    assert validated['name'] == 'Rect'
    assert validated['expression'] == 'a * b'
    assert validated['extra'] == 1

# ** test: schema_missing_required_raises
def test_schema_missing_required_raises():
    '''
    Missing a required parameter raises REQUEST_VALIDATION_FAILED.
    '''

    # Build a schema requiring name and expression.
    schema = RequestSpecification.model_validate({'name': 'str', 'expression': 'str'})

    # Omitting a required parameter raises a structured validation error.
    with pytest.raises(TiferetError) as exc_info:
        schema.validate({'name': 'Rect'}, feature_id='formula.save')
    assert exc_info.value.error_code == 'REQUEST_VALIDATION_FAILED'
