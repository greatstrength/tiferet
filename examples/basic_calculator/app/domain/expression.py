# *** imports

# ** core
from typing import Callable, List

# ** infra
from pydantic import Field

# ** app
from tiferet import DomainObject
from ..assets.core import OPERATOR_PRECEDENCE

# *** models

# ** model: expression
class Expression(DomainObject):
    '''
    A fully-logged, precedence-aware calculator expression: the flat
    operand/operator term list accumulated over an entire fluent chain,
    resolved to its final value in a single deferred pass (see ``resolve``)
    rather than incrementally as each term is logged.
    '''

    # * attribute: values
    values: List[float] = Field(default_factory=list, description='The full operand list, leading operand first.')

    # * attribute: operators
    operators: List[str] = Field(default_factory=list, description='The full operator list, one per operand after the first.')

    # * method: display
    def display(self) -> str:
        '''
        Render the expression as an infix string (e.g. "4 - 5 * 2").

        :return: The rendered infix expression, or an empty string when no
            values are logged.
        :rtype: str
        '''

        # Return an empty string when nothing has been logged yet.
        if not self.values:
            return ''

        # Render the leading operand, then interleave each operator/operand pair.
        rendered = str(self.values[0])
        for operator, operand in zip(self.operators, self.values[1:]):
            rendered += f' {operator} {operand}'

        # Return the rendered infix expression.
        return rendered

    # * method: resolve
    def resolve(self, reduce: Callable[[str, float, float], float]) -> float:
        '''
        Resolve the fully-logged expression into a single value.

        Implements standard PEMDAS scheduling via operator-precedence
        ("shunting yard") reduction, performed in one deferred pass over the
        complete term list rather than incrementally as each term arrives --
        logging a term (see ``FluentRequestContext.log_term``) is a plain
        append with no reduction; this method does the entire scheduling
        pass in one call, at the very end. The actual ``left op right``
        computation is delegated to the caller-supplied ``reduce`` callable,
        so this domain object never learns how a reduction is computed.

        :param reduce: A callable computing ``operator(left, right)``.
        :type reduce: Callable[[str, float, float], float]
        :return: The single, fully-reduced value.
        :rtype: float
        '''

        # Start from the leading operand; nothing pending yet.
        pending_values = [self.values[0]]
        pending_operators: List[str] = []

        # Fold in every subsequent operator/operand pair.
        for operator, operand in zip(self.operators, self.values[1:]):

            # Reduce any pending operator that binds at least as tightly as the incoming one.
            while pending_operators and OPERATOR_PRECEDENCE[pending_operators[-1]] >= OPERATOR_PRECEDENCE[operator]:
                top_operator = pending_operators.pop()
                right = pending_values.pop()
                left = pending_values.pop()
                pending_values.append(reduce(top_operator, left, right))

            # Push the incoming operator/operand pair.
            pending_operators.append(operator)
            pending_values.append(operand)

        # Drain every remaining pending operator, lowest precedence last.
        while pending_operators:
            top_operator = pending_operators.pop()
            right = pending_values.pop()
            left = pending_values.pop()
            pending_values.append(reduce(top_operator, left, right))

        # Return the single remaining, fully-reduced value.
        return pending_values[0]
