"""Tiferet Basic Calculator Formula Mapper Tests"""

# *** imports

# ** infra
import pytest

# ** app
from tiferet import TiferetError
from app.mappers.formula import FormulaAggregate, FormulaConfigObject

# *** tests

# ** test: aggregate_derives_id_and_variables
def test_aggregate_derives_id_and_variables():
    '''
    Constructing an aggregate derives the id and infers the variables.
    '''

    # Build an aggregate from a name and expression.
    formula = FormulaAggregate(name='Rectangle Area', expression='width * height')

    # The id is snake_cased and the variables are inferred from the expression.
    assert formula.id == 'rectangle_area'
    assert formula.variables == ['width', 'height']

# ** test: aggregate_set_expression_reinfers_variables
def test_aggregate_set_expression_reinfers_variables():
    '''
    Updating the expression re-derives the variable list.
    '''

    # Update the expression on an existing aggregate.
    formula = FormulaAggregate(name='Rectangle Area', expression='width * height')
    formula.set_expression('base + offset')

    # The variables reflect the new expression.
    assert formula.variables == ['base', 'offset']

# ** test: aggregate_set_attribute_invalid
def test_aggregate_set_attribute_invalid():
    '''
    Setting an unknown attribute raises a structured error.
    '''

    # Attempt to set an unknown attribute.
    formula = FormulaAggregate(name='Rectangle Area', expression='width * height')
    with pytest.raises(TiferetError) as exc_info:
        formula.set_attribute('not_a_field', 'value')

    # The error code identifies the invalid attribute.
    assert exc_info.value.error_code == 'INVALID_MODEL_ATTRIBUTE'

# ** test: config_object_map
def test_config_object_map():
    '''
    A config object maps to an aggregate with the id supplied externally.
    '''

    # Validate YAML-shaped data (id provided by the repository key).
    config = FormulaConfigObject.model_validate({
        'id': 'rectangle_area',
        'name': 'Rectangle Area',
        'expression': 'width * height',
        'variables': ['width', 'height'],
    })

    # Mapping produces a FormulaAggregate with matching fields.
    formula = config.map()
    assert isinstance(formula, FormulaAggregate)
    assert formula.id == 'rectangle_area'
    assert formula.expression == 'width * height'

# ** test: config_object_round_trip
def test_config_object_round_trip():
    '''
    Aggregate -> config object -> aggregate preserves the formula data.
    '''

    # Start from an aggregate and convert it to persisted data.
    original = FormulaAggregate(name='Rectangle Area', expression='width * height')
    data = FormulaConfigObject.from_model(original).to_primitive('to_data')

    # The id is excluded from the persisted data (it is the mapping key).
    assert 'id' not in data

    # Rebuild the aggregate from the persisted data plus the key id.
    rebuilt = FormulaConfigObject.model_validate({**data, 'id': original.id}).map()
    assert rebuilt.id == original.id
    assert rebuilt.expression == original.expression
    assert rebuilt.variables == original.variables

# ** test: aggregate_display
def test_aggregate_display():
    '''
    The display string is human-readable and backs __str__.
    '''

    # Build an aggregate and render its display string.
    formula = FormulaAggregate(name='Rectangle Area', expression='width * height')

    # The display reads naturally and __str__ matches it.
    assert formula.display() == 'Rectangle Area: width * height (variables: width, height)'
    assert str(formula) == formula.display()
