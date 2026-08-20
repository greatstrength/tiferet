# *** imports

# ** core
from typing import Callable

# ** app
from tiferet.contexts.core import BaseContext
from tiferet.contexts.cache import CacheContext
from ..assets.core import CALC_EXPRESSION_CACHE_PREFIX, OPERATOR_PRECEDENCE
from ..domain.expression import Expression, ExpressionState

# *** contexts

# ** context: expression_context
class ExpressionContext(BaseContext):
    '''
    The expression context is the calculator's "in-flight request" context:
    it plays the same role RequestContext plays for a single feature call,
    but scoped to one in-progress, precedence-aware fluent expression cached
    across multiple chained calls.
    '''

    # * attribute: domain_type
    domain_type = Expression

    # * method: load (static)
    @classmethod
    def load(cls, cache: CacheContext, expression_id: str) -> 'ExpressionContext':
        '''
        Load the cached expression for an id, or start a fresh, empty one.

        :param cache: The shared cache context to read from.
        :type cache: CacheContext
        :param expression_id: The unique identifier of the fluent chain.
        :type expression_id: str
        :return: The expression context bound to the loaded or new expression.
        :rtype: ExpressionContext
        '''

        # Retrieve the cached expression, falling back to a fresh, empty one.
        cached = cache.get(expression_id, *CALC_EXPRESSION_CACHE_PREFIX)
        expression = cached if cached is not None else Expression(id=expression_id)

        # Return the expression context bound to the resolved expression.
        return cls.from_domain(expression)

    # * method: save
    def save(self, cache: CacheContext) -> None:
        '''
        Write the bound expression back into the shared cache.

        :param cache: The shared cache context to write to.
        :type cache: CacheContext
        '''

        # Store the bound expression under its own id.
        cache.set(self.domain.id, self.domain, *CALC_EXPRESSION_CACHE_PREFIX)

    # * method: discard
    def discard(self, cache: CacheContext) -> None:
        '''
        Remove the bound expression from the shared cache. Idempotent.

        :param cache: The shared cache context to remove from.
        :type cache: CacheContext
        '''

        # Remove the cached expression entry, if any.
        cache.delete(self.domain.id, *CALC_EXPRESSION_CACHE_PREFIX)

    # * method: start
    def start(self, value: float) -> None:
        '''
        Seed the expression with its first pending operand.

        :param value: The initial operand of a new fluent chain.
        :type value: float
        '''

        # Seed the pending operand stack; clear any stale operator stack.
        self.domain.values = [float(value)]
        self.domain.operators = []

    # * method: _snapshot (private)
    def _snapshot(self, label: str) -> None:
        '''
        Append a labeled snapshot of the current pending stacks to history.

        :param label: A human-readable description of this snapshot.
        :type label: str
        '''

        # Append a copy of the current stacks so later mutation cannot alias it.
        self.domain.history.append(
            ExpressionState(
                label=label,
                values=list(self.domain.values),
                operators=list(self.domain.operators),
            )
        )

    # * method: apply_term
    def apply_term(self,
            operator: str,
            operand: float,
            reduce: Callable[[str, float, float], float]) -> None:
        '''
        Fold a new operator/operand pair into the pending expression.

        Implements operator-precedence (\"shunting yard\") scheduling: any
        pending operator whose precedence is greater than or equal to the
        incoming operator's is reduced first (left-associative), via the
        caller-supplied ``reduce`` callable, before the new term is pushed.
        This is what lets a lower-precedence operator (e.g. \"-\") wait for a
        higher-precedence one that arrives after it (e.g. \"*\") to be applied
        first, matching standard PEMDAS evaluation order.

        :param operator: The incoming operator symbol.
        :type operator: str
        :param operand: The incoming operand.
        :type operand: float
        :param reduce: A callable computing ``operator(left, right)``, wired
            by the caller to dispatch through the real arithmetic feature.
        :type reduce: Callable[[str, float, float], float]
        '''

        # Reduce any pending operator that binds at least as tightly as the incoming one.
        while self.domain.operators and OPERATOR_PRECEDENCE[self.domain.operators[-1]] >= OPERATOR_PRECEDENCE[operator]:
            top_operator = self.domain.operators.pop()
            right = self.domain.values.pop()
            left = self.domain.values.pop()

            # Compute the reduction via the caller-supplied callable and push the result back.
            reduced = reduce(top_operator, left, right)
            self.domain.values.append(reduced)
            self._snapshot(f'{left} {top_operator} {right} = {reduced}')

        # Push the incoming operator/operand pair and snapshot the new pending state.
        self.domain.operators.append(operator)
        self.domain.values.append(float(operand))
        self._snapshot(f'pushed {operator} {operand}')

    # * method: finalize
    def finalize(self, reduce: Callable[[str, float, float], float]) -> float:
        '''
        Drain every remaining pending operator and return the final value.

        :param reduce: A callable computing ``operator(left, right)``, wired
            by the caller to dispatch through the real arithmetic feature.
        :type reduce: Callable[[str, float, float], float]
        :return: The single remaining, fully-reduced value.
        :rtype: float
        '''

        # Reduce every remaining pending operator, lowest in the stack last.
        while self.domain.operators:
            top_operator = self.domain.operators.pop()
            right = self.domain.values.pop()
            left = self.domain.values.pop()

            # Compute the reduction via the caller-supplied callable and push the result back.
            reduced = reduce(top_operator, left, right)
            self.domain.values.append(reduced)
            self._snapshot(f'{left} {top_operator} {right} = {reduced}')

        # Return the single remaining, fully-reduced value.
        return self.domain.values[0]

    # * attribute: history
    @property
    def history(self):
        '''
        The recorded snapshot history of this expression.

        :return: The ordered list of expression state snapshots.
        :rtype: list
        '''

        # Return the bound expression's history.
        return self.domain.history

    # * method: display
    def display(self) -> str:
        '''
        Render the pending expression as an infix string.

        :return: The rendered infix expression.
        :rtype: str
        '''

        # Delegate to the bound expression's display method.
        return self.domain.display()
