# *** imports

# ** core
from typing import List

# ** infra
from pydantic import Field

# ** app
from tiferet import DomainObject

# *** models

# ** model: expression_state
class ExpressionState(DomainObject):
    '''
    A read-only snapshot of an in-progress calculator expression, captured
    after every fluent operation so a PEMDAS-aware evaluator can explain (or
    replay) how a result was reached.
    '''

    # * attribute: label
    label: str = Field(..., description='A human-readable description of this snapshot.')

    # * attribute: values
    values: List[float] = Field(default_factory=list, description='The pending operand stack at this point.')

    # * attribute: operators
    operators: List[str] = Field(default_factory=list, description='The pending operator stack at this point, lowest precedence at the bottom.')

# ** model: expression
class Expression(DomainObject):
    '''
    An in-progress, precedence-aware calculator expression built one fluent
    operation at a time and cached between chained calls.
    '''

    # * attribute: id
    id: str = Field(..., description='The unique identifier of the expression (one per fluent chain).')

    # * attribute: values
    values: List[float] = Field(default_factory=list, description='The pending operand stack.')

    # * attribute: operators
    operators: List[str] = Field(default_factory=list, description='The pending operator stack, lowest precedence at the bottom.')

    # * attribute: history
    history: List[ExpressionState] = Field(default_factory=list, description='Snapshots recorded after each fluent operation, oldest first.')

    # * method: display
    def display(self) -> str:
        '''
        Render the pending expression as an infix string (e.g. "4 - 5 * 2").

        :return: The rendered infix expression, or an empty string when no
            values are pending.
        :rtype: str
        '''

        # Return an empty string when nothing has been pushed yet.
        if not self.values:
            return ''

        # Render the leading operand, then interleave each operator/operand pair.
        rendered = str(self.values[0])
        for operator, operand in zip(self.operators, self.values[1:]):
            rendered += f' {operator} {operand}'

        # Return the rendered infix expression.
        return rendered
