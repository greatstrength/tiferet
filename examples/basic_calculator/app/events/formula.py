# *** imports

# ** core
import json
from typing import Any, Dict

# ** infra
from tiferet.events import DomainEvent

# ** app
from ..interfaces.formula import FormulaService
from ..mappers.formula import FormulaAggregate

# *** events

# ** event: formula_event
class FormulaEvent(DomainEvent):
    '''
    Base event providing the shared FormulaService dependency for formula
    domain events.
    '''

    # * attribute: formula_service
    formula_service: FormulaService

    # * init
    def __init__(self, formula_service: FormulaService):
        '''
        Initialize the formula event with its shared service dependency.

        :param formula_service: The formula service shared across formula events.
        :type formula_service: FormulaService
        '''

        # Set the formula service dependency.
        self.formula_service = formula_service

    # * method: coerce_number
    def coerce_number(self, value: Any) -> int | float:
        '''
        Convert a value to an int or float, raising INVALID_INPUT on failure.

        :param value: The value to convert.
        :type value: Any
        :return: The numeric value.
        :rtype: int | float
        '''

        # Attempt to convert the value to an int or float.
        try:
            text = str(value)
            return float(text) if '.' in text else int(text)

        # Raise a structured error when the value is not numeric.
        except (ValueError, TypeError):
            self.raise_error(
                'INVALID_INPUT',
                f'Value {value} must be a number',
                value=value,
            )

# ** event: save_formula
class SaveFormula(FormulaEvent):
    '''
    Event to save (create or update) a formula.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['name', 'expression'])
    def execute(self,
            name: str,
            expression: str,
            description: str | None = None,
            **kwargs,
        ) -> FormulaAggregate:
        '''
        Save a formula and return it.

        :param name: The human-readable name of the formula.
        :type name: str
        :param expression: The arithmetic expression using named variables.
        :type expression: str
        :param description: An optional description of the formula.
        :type description: str | None
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The saved formula aggregate.
        :rtype: FormulaAggregate
        '''

        # Create the formula aggregate (id and variables are derived).
        formula = FormulaAggregate(
            name=name,
            expression=expression,
            description=description,
        )

        # Persist the formula (save is an upsert).
        self.formula_service.save(formula)

        # Return the saved formula.
        return formula

# ** event: get_formula
class GetFormula(FormulaEvent):
    '''
    Event to retrieve a formula by its ID.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> FormulaAggregate:
        '''
        Retrieve a formula by ID.

        :param id: The unique identifier of the formula.
        :type id: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The formula aggregate.
        :rtype: FormulaAggregate
        '''

        # Retrieve the formula from the service.
        formula = self.formula_service.get(id)

        # Verify that the formula exists.
        self.verify(
            formula is not None,
            'FORMULA_NOT_FOUND',
            f'Formula not found: {id}',
            id=id,
        )

        # Return the retrieved formula.
        return formula

# ** event: list_formulas
class ListFormulas(FormulaEvent):
    '''
    Event to list all saved formulas as a friendly, human-readable view.
    '''

    # * method: execute
    def execute(self, **kwargs) -> str:
        '''
        List all saved formulas as a rendered, human-readable string.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A newline-separated summary of the saved formulas.
        :rtype: str
        '''

        # Retrieve all formulas from the service.
        formulas = self.formula_service.list()

        # Return a friendly message when there are no saved formulas.
        if not formulas:
            return 'No formulas saved yet.'

        # Render each formula on its own line.
        return '\n'.join(formula.display() for formula in formulas)

# ** event: evaluate_formula
class EvaluateFormula(FormulaEvent):
    '''
    Event to evaluate a saved formula with concrete variable values.
    '''

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, values: Any = None, **kwargs) -> int | float:
        '''
        Evaluate a saved formula by substituting concrete variable values.

        :param id: The unique identifier of the formula.
        :type id: str
        :param values: A mapping (or JSON string) of variable names to values.
        :type values: Any
        :param kwargs: Additional keyword arguments (may carry variables directly).
        :type kwargs: dict
        :return: The evaluated numeric result.
        :rtype: int | float
        '''

        # Retrieve the formula and verify it exists.
        formula = self.formula_service.get(id)
        self.verify(
            formula is not None,
            'FORMULA_NOT_FOUND',
            f'Formula not found: {id}',
            id=id,
        )

        # Parse a JSON-encoded values mapping when provided as a string.
        if isinstance(values, str):
            values = json.loads(values)

        # Collect provided values from the mapping and any direct kwargs.
        provided: Dict[str, Any] = dict(values or {})
        for variable in formula.variables:
            if variable not in provided and variable in kwargs:
                provided[variable] = kwargs[variable]

        # Verify every required variable is present and coerce it to a number.
        resolved: Dict[str, int | float] = {}
        for variable in formula.variables:
            self.verify(
                variable in provided,
                'MISSING_VARIABLE',
                f'Missing value for variable: {variable}',
                variable=variable,
            )
            resolved[variable] = self.coerce_number(provided[variable])

        # Evaluate the expression with restricted globals (no builtins exposed).
        try:
            result = eval(formula.expression, {'__builtins__': {}}, resolved)  # noqa: S307

        # Wrap evaluation failures in a structured error.
        except Exception as e:
            self.raise_error(
                'FORMULA_EVALUATION_FAILED',
                f'Could not evaluate formula {id}: {e}',
                id=id,
                error=str(e),
            )

        # Return the evaluated result.
        return result
