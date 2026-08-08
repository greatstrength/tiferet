"""Tiferet Basic Calculator Request Schema Tests"""

# *** imports

# ** infra
import pytest
from pydantic import ValidationError

# ** app
from tiferet.domain.feature import RequestSpecification

# *** tests

# ** test: schema_validates_and_coerces
def test_schema_validates_and_coerces():
    '''
    A request schema coerces declared parameters and preserves extras.
    '''

    # Build a schema mirroring the formula.save feature.
    schema = RequestSpecification.model_validate({'name': 'str', 'expression': 'str'})

    # Coercion returns the coerced data, preserving unspecified keys.
    validated = schema.coerce({'name': 'Rect', 'expression': 'a * b', 'extra': 1})
    assert validated['name'] == 'Rect'
    assert validated['expression'] == 'a * b'
    assert validated['extra'] == 1

# ** test: schema_missing_required_raises
def test_schema_missing_required_raises():
    '''
    Missing a required parameter raises the pydantic validation error; naming it
    REQUEST_VALIDATION_FAILED is the feature context's concern.
    '''

    # Build a schema requiring name and expression.
    schema = RequestSpecification.model_validate({'name': 'str', 'expression': 'str'})

    # Omitting a required parameter raises a validation error for the field.
    with pytest.raises(ValidationError) as exc_info:
        schema.coerce({'name': 'Rect'})
    assert exc_info.value.errors()[0]['loc'] == ('expression',)
