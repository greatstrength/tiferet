# *** imports

# ** core
import re
from typing import Any, ClassVar, Dict

# ** app
from tiferet.mappers import Aggregate, TransferObject
from ..domain.formula import Formula

# *** mappers

# ** mapper: formula_aggregate
class FormulaAggregate(Formula, Aggregate):
    '''
    An aggregate representation of a formula.
    '''

    # * method: rename
    def rename(self, new_name: str) -> None:
        '''
        Renames the formula.

        :param new_name: The new name for the formula.
        :type new_name: str
        :return: None
        :rtype: None
        '''

        # Update the name; validate_assignment=True handles re-validation.
        self.name = new_name

    # * method: set_expression
    def set_expression(self, expression: str) -> None:
        '''
        Updates the expression and re-derives the variable list.

        :param expression: The new arithmetic expression.
        :type expression: str
        :return: None
        :rtype: None
        '''

        # Update the expression.
        self.expression = expression

        # Re-derive the variables from the new expression identifiers.
        identifiers = re.findall(r'[A-Za-z_][A-Za-z0-9_]*', expression)
        self.variables = list(dict.fromkeys(identifiers))


# ** mapper: formula_config_object
class FormulaConfigObject(Formula, TransferObject):
    '''
    A configuration data representation of a formula object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {},
        'to_data': {'by_alias': True, 'exclude': {'id'}},
    }

    # * method: map
    def map(self, **overrides) -> FormulaAggregate:
        '''
        Maps the formula data to a formula aggregate.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new formula aggregate.
        :rtype: FormulaAggregate
        '''

        # Map the formula data to the aggregate.
        return super().map(FormulaAggregate, **overrides)
