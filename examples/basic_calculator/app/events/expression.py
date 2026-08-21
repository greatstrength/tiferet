# *** imports

# ** core
from typing import Any, List

# ** infra
from tiferet.events import DomainEvent

# ** app
from ..assets.core import ADD_OPERATOR, SUBTRACT_OPERATOR, MULTIPLY_OPERATOR, DIVIDE_OPERATOR
from ..domain.expression import Expression

# *** events

# ** event: resolve_expression
class ResolveExpression(DomainEvent):
    '''
    Resolves a fully-logged fluent expression -- the flat values/operators
    term list accumulated on a FluentRequestContext over an entire chain --
    into its final numeric value in one feature run.

    Each pairwise reduction still dispatches through the calculator's own
    arithmetic events, constructor-injected here as siblings resolved from
    the same bounded-context service container (the four are already
    registered by CALC_DEFAULT_SERVICES under exactly these ids), so input
    validation and division-by-zero handling are reused completely
    unchanged -- none of it is reinvented here. Only the PEMDAS scheduling
    itself, delegated to Expression.resolve, is this event's own concern.
    '''

    # * init
    def __init__(self,
            add_number_event: DomainEvent,
            subtract_number_event: DomainEvent,
            multiply_number_event: DomainEvent,
            divide_number_event: DomainEvent):
        '''
        Initialize the event with its sibling arithmetic event dependencies.

        :param add_number_event: The addition event.
        :type add_number_event: DomainEvent
        :param subtract_number_event: The subtraction event.
        :type subtract_number_event: DomainEvent
        :param multiply_number_event: The multiplication event.
        :type multiply_number_event: DomainEvent
        :param divide_number_event: The division event.
        :type divide_number_event: DomainEvent
        '''

        # Map each operator symbol to the arithmetic event that implements it.
        self._operator_events = {
            ADD_OPERATOR: add_number_event,
            SUBTRACT_OPERATOR: subtract_number_event,
            MULTIPLY_OPERATOR: multiply_number_event,
            DIVIDE_OPERATOR: divide_number_event,
        }

    # * method: execute
    def execute(self, values: List[float], operators: List[str], **kwargs) -> Any:
        '''
        Resolve the logged expression into its final numeric value.

        :param values: The full operand list, leading operand first.
        :type values: List[float]
        :param operators: The full operator list.
        :type operators: List[str]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The fully-reduced numeric result.
        :rtype: Any
        '''

        # Build the expression from the logged terms and resolve it in one pass.
        expression = Expression(values=values, operators=operators)
        return expression.resolve(reduce=self._reduce)

    # * method: _reduce (private)
    def _reduce(self, operator: str, left: float, right: float) -> Any:
        '''
        Compute a single pairwise reduction, passed to Expression.resolve as
        its ``reduce`` callable.

        :param operator: The operator symbol to reduce.
        :type operator: str
        :param left: The left operand.
        :type left: float
        :param right: The right operand.
        :type right: float
        :return: The result of the underlying arithmetic event.
        :rtype: Any
        '''

        # Delegate to the operator-lookup helper.
        return self.execute_operator(operator, left, right)

    # * method: execute_operator
    def execute_operator(self, operator: str, left: float, right: float) -> Any:
        '''
        Look up the arithmetic event mapped to an operator symbol and
        execute it against a pair of operands.

        Wrapping the ``_operator_events`` dictionary lookup in its own
        method keeps ``_reduce`` a plain adapter for ``Expression.resolve``
        and gives the lookup itself a name that can be tested or overridden
        independently.

        :param operator: The operator symbol to look up.
        :type operator: str
        :param left: The left operand.
        :type left: float
        :param right: The right operand.
        :type right: float
        :return: The result of the underlying arithmetic event.
        :rtype: Any
        '''

        # Resolve the arithmetic event mapped to this operator and execute it.
        event = self._operator_events[operator]
        return event.execute(a=left, b=right)
