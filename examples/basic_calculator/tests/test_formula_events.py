"""Tiferet Basic Calculator Formula Event Tests"""

# *** imports

# ** core
from unittest import mock

# ** infra
import pytest

# ** app
from tiferet import TiferetError
from tiferet.events import DomainEvent
from app.interfaces.formula import FormulaService
from app.mappers.formula import FormulaAggregate
from app.events.formula import (
    SaveFormula,
    GetFormula,
    ListFormulas,
    EvaluateFormula,
)

# *** fixtures

# ** fixture: mock_formula_service
@pytest.fixture
def mock_formula_service() -> FormulaService:
    '''
    A mocked formula service.
    '''

    # Return a mock conforming to the FormulaService interface.
    return mock.Mock(spec=FormulaService)

# ** fixture: sample_formula
@pytest.fixture
def sample_formula() -> FormulaAggregate:
    '''
    A sample rectangle-area formula aggregate.
    '''

    # Build a sample formula with inferred id and variables.
    return FormulaAggregate(name='Rectangle Area', expression='width * height')

# *** tests

# ** test: save_formula
def test_save_formula(mock_formula_service):
    '''
    Saving a formula creates an aggregate and persists it.
    '''

    # Execute the save event via the static handle interface.
    result = DomainEvent.handle(
        SaveFormula,
        dependencies={'formula_service': mock_formula_service},
        name='Rectangle Area',
        expression='width * height',
    )

    # The aggregate is created, persisted, and returned.
    assert result.id == 'rectangle_area'
    assert result.variables == ['width', 'height']
    mock_formula_service.save.assert_called_once()

# ** test: get_formula_success
def test_get_formula_success(mock_formula_service, sample_formula):
    '''
    Retrieving an existing formula returns it.
    '''

    # Arrange the service to return the sample formula.
    mock_formula_service.get.return_value = sample_formula

    # Execute the get event.
    result = DomainEvent.handle(
        GetFormula,
        dependencies={'formula_service': mock_formula_service},
        id='rectangle_area',
    )

    # The sample formula is returned.
    assert result is sample_formula

# ** test: get_formula_not_found
def test_get_formula_not_found(mock_formula_service):
    '''
    Retrieving a missing formula raises FORMULA_NOT_FOUND.
    '''

    # Arrange the service to return None.
    mock_formula_service.get.return_value = None

    # Executing the get event raises a structured error.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            GetFormula,
            dependencies={'formula_service': mock_formula_service},
            id='nope',
        )
    assert exc_info.value.error_code == 'FORMULA_NOT_FOUND'

# ** test: list_formulas
def test_list_formulas(mock_formula_service, sample_formula):
    '''
    Listing formulas renders a friendly summary of the service results.
    '''

    # Arrange the service to return a list with one formula.
    mock_formula_service.list.return_value = [sample_formula]

    # Execute the list event.
    result = DomainEvent.handle(
        ListFormulas,
        dependencies={'formula_service': mock_formula_service},
    )

    # The rendered summary includes the formula name and expression.
    assert result == 'Rectangle Area: width * height (variables: width, height)'

# ** test: list_formulas_empty
def test_list_formulas_empty(mock_formula_service):
    '''
    Listing formulas returns a friendly message when none are saved.
    '''

    # Arrange the service to return no formulas.
    mock_formula_service.list.return_value = []

    # Execute the list event.
    result = DomainEvent.handle(
        ListFormulas,
        dependencies={'formula_service': mock_formula_service},
    )

    # A friendly empty message is returned.
    assert result == 'No formulas saved yet.'

# ** test: evaluate_formula_success
def test_evaluate_formula_success(mock_formula_service, sample_formula):
    '''
    Evaluating a formula substitutes values and returns the numeric result.
    '''

    # Arrange the service to return the sample formula.
    mock_formula_service.get.return_value = sample_formula

    # Execute the evaluate event with concrete values.
    result = DomainEvent.handle(
        EvaluateFormula,
        dependencies={'formula_service': mock_formula_service},
        id='rectangle_area',
        values={'width': 3, 'height': 4},
    )

    # The expression evaluates with the substituted values.
    assert result == 12

# ** test: evaluate_formula_missing_variable
def test_evaluate_formula_missing_variable(mock_formula_service, sample_formula):
    '''
    Evaluating without all variables raises MISSING_VARIABLE.
    '''

    # Arrange the service to return the sample formula.
    mock_formula_service.get.return_value = sample_formula

    # Executing without a required variable raises a structured error.
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            EvaluateFormula,
            dependencies={'formula_service': mock_formula_service},
            id='rectangle_area',
            values={'width': 3},
        )
    assert exc_info.value.error_code == 'MISSING_VARIABLE'
