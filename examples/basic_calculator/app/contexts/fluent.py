# *** imports

# ** core
from typing import Any, Dict, List, Tuple

# ** app
from tiferet.contexts.request import RequestContext
from .. import assets as a
from ..domain.expression import Expression
from .calc import CalculatorAppContext

# *** contexts

# ** context: fluent_request_context
class FluentRequestContext(RequestContext):
    '''
    A specialized ``RequestContext`` for the fluent calculator chain,
    mirroring the precedent of ``CliRequestContext``'s specialization for
    one entry point.

    A fluent chain is not many requests correlated by a shared id; it is
    one request with many steps, so the chain's accumulated operand/operator
    terms are logged directly onto this single, persistent request's own
    ``data`` payload -- the same ``request.data`` the eventual
    ``calc.resolve`` step reads its ``values``/``operators`` kwargs from.
    '''

    # * method: start
    def start(self, value: float) -> None:
        '''
        Seed the request with the leading operand of a new chain.

        :param value: The initial operand.
        :type value: float
        '''

        # Seed the operand list; clear any stale operator list.
        self.data['values'] = [float(value)]
        self.data['operators'] = []

    # * method: log_term
    def log_term(self, operator: str, operand: float) -> None:
        '''
        Log one more operator/operand pair onto the accumulating chain.

        Performs no reduction -- this is a plain append. All PEMDAS
        scheduling is deferred entirely to ``Expression.resolve``, run once
        when the chain finalizes.

        :param operator: The incoming operator symbol.
        :type operator: str
        :param operand: The incoming operand.
        :type operand: float
        '''

        # Append the incoming operator/operand pair.
        self.data.setdefault('operators', []).append(operator)
        self.data.setdefault('values', []).append(float(operand))

    # * attribute: terms
    @property
    def terms(self) -> Tuple[List[float], List[str]]:
        '''
        The logged operand/operator term lists.

        :return: A (values, operators) tuple.
        :rtype: Tuple[List[float], List[str]]
        '''

        # Return the logged term lists, defaulting to empty when unset.
        return list(self.data.get('values', [])), list(self.data.get('operators', []))

# ** context: calculator_fluent_context
class CalculatorFluentContext(CalculatorAppContext):
    '''
    The fluent, chainable calculator surface: every operator exposes two
    distinct methods -- a starter (two operands, begins a new expression)
    and a continuation (one operand, folds into the already-active
    expression) -- and every call only logs a term onto the persistent
    ``FluentRequestContext`` held for the whole chain. Nothing is
    dispatched or recorded until ``run()`` collapses the entire chain into
    a single ``calc.resolve`` feature run (see ``run`` below).
    '''

    # * attribute: pending_request (private)
    _pending_request: FluentRequestContext | None

    # * init
    def __init__(self, *args, **kwargs):
        '''
        Initialize the fluent calculator context.

        Forwards every argument to ``CalculatorAppContext`` unchanged; this
        subclass adds only the chain's own pending-request state.

        :param args: Positional arguments forwarded to ``CalculatorAppContext``.
        :type args: tuple
        :param kwargs: Keyword arguments forwarded to ``CalculatorAppContext``.
        :type kwargs: dict
        '''

        # Initialize the inherited client/record_run surface.
        super().__init__(*args, **kwargs)

        # No chain is active until the first starter method is called.
        self._pending_request = None

    # * method: build_request
    def build_request(self,
            feature_id: str,
            headers: Dict[str, str] = {},
            data: Dict[str, Any] = {}) -> RequestContext:
        '''
        Return the active chain's own persistent request instead of
        building a fresh one, when a chain is in progress.

        This is the seam that collapses an entire fluent chain into exactly
        one ``run()`` call: by the time ``run()`` calls
        ``super().run('calc.resolve', ...)`` (see below), every intermediate
        ``.add()``/``.add_to()``/etc. call has already logged its term
        directly onto this same persistent request, so resolving it takes
        one logger build, one ``execute_feature`` call, and one
        ``record_run`` entry.

        :param feature_id: The identifier of the feature to execute.
        :type feature_id: str
        :param headers: The request headers.
        :type headers: Dict[str, str]
        :param data: The request data.
        :type data: Dict[str, Any]
        :return: The active chain's request, or a freshly built one.
        :rtype: RequestContext
        '''

        # Return the active chain's own persistent request when one exists.
        if self._pending_request is not None:
            self._pending_request.feature_id = feature_id
            return self._pending_request

        # Otherwise build a fresh request via the inherited hub.
        return super().build_request(feature_id, headers, data)

    # * method: _start (private)
    def _start(self, operator: str, first: float, second: float) -> 'CalculatorFluentContext':
        '''
        Begin a brand-new expression from two operands.

        :param operator: The operator joining the two operands.
        :type operator: str
        :param first: The first (leading) operand.
        :type first: float
        :param second: The second operand.
        :type second: float
        :return: This context, for further chaining.
        :rtype: CalculatorFluentContext
        '''

        # Refuse to clobber an already-active chain.
        self._guard(self._pending_request is None, a.core.EXPRESSION_ALREADY_ACTIVE_ID)

        # Start a fresh, persistent request and log the first term.
        self._pending_request = FluentRequestContext()
        self._pending_request.start(first)
        self._pending_request.log_term(operator, second)

        # Return self so the caller may keep chaining.
        return self

    # * method: _continue (private)
    def _continue(self, operator: str, operand: float) -> 'CalculatorFluentContext':
        '''
        Fold one more operand into the already-active chain.

        :param operator: The operator joining the operand to the running expression.
        :type operator: str
        :param operand: The next operand.
        :type operand: float
        :return: This context, for further chaining.
        :rtype: CalculatorFluentContext
        '''

        # Require an active chain to continue.
        self._guard(self._pending_request is not None, a.core.NO_ACTIVE_EXPRESSION_ID)

        # Log the term onto the active chain's persistent request.
        self._pending_request.log_term(operator, operand)

        # Return self so the caller may keep chaining.
        return self

    # * method: add
    def add(self, a_value: float, b_value: float) -> 'CalculatorFluentContext':
        '''
        Begin a new expression by adding two operands.

        :param a_value: The first operand.
        :type a_value: float
        :param b_value: The second operand.
        :type b_value: float
        :return: This context, for further chaining.
        :rtype: CalculatorFluentContext
        '''

        # Start a new expression with the '+' operator.
        return self._start(a.core.ADD_OPERATOR, a_value, b_value)

    # * method: add_to
    def add_to(self, value: float) -> 'CalculatorFluentContext':
        '''
        Continue the active expression by adding one more operand.

        :param value: The operand to add next.
        :type value: float
        :return: This context, for further chaining.
        :rtype: CalculatorFluentContext
        '''

        # Continue the active expression with the '+' operator.
        return self._continue(a.core.ADD_OPERATOR, value)

    # * method: subtract
    def subtract(self, a_value: float, b_value: float) -> 'CalculatorFluentContext':
        '''
        Begin a new expression by subtracting the second operand from the first.

        :param a_value: The first operand.
        :type a_value: float
        :param b_value: The second operand.
        :type b_value: float
        :return: This context, for further chaining.
        :rtype: CalculatorFluentContext
        '''

        # Start a new expression with the '-' operator.
        return self._start(a.core.SUBTRACT_OPERATOR, a_value, b_value)

    # * method: subtract_from
    def subtract_from(self, value: float) -> 'CalculatorFluentContext':
        '''
        Continue the active expression by subtracting one more operand.

        Despite the name, this appends "- value" to the running expression
        (continuing left-to-right) -- it does not compute "value - current".

        :param value: The operand to subtract next.
        :type value: float
        :return: This context, for further chaining.
        :rtype: CalculatorFluentContext
        '''

        # Continue the active expression with the '-' operator.
        return self._continue(a.core.SUBTRACT_OPERATOR, value)

    # * method: multiply
    def multiply(self, a_value: float, b_value: float) -> 'CalculatorFluentContext':
        '''
        Begin a new expression by multiplying two operands.

        :param a_value: The first operand.
        :type a_value: float
        :param b_value: The second operand.
        :type b_value: float
        :return: This context, for further chaining.
        :rtype: CalculatorFluentContext
        '''

        # Start a new expression with the '*' operator.
        return self._start(a.core.MULTIPLY_OPERATOR, a_value, b_value)

    # * method: multiply_by
    def multiply_by(self, value: float) -> 'CalculatorFluentContext':
        '''
        Continue the active expression by multiplying by one more operand.

        :param value: The operand to multiply by next.
        :type value: float
        :return: This context, for further chaining.
        :rtype: CalculatorFluentContext
        '''

        # Continue the active expression with the '*' operator.
        return self._continue(a.core.MULTIPLY_OPERATOR, value)

    # * method: divide
    def divide(self, a_value: float, b_value: float) -> 'CalculatorFluentContext':
        '''
        Begin a new expression by dividing the first operand by the second.

        :param a_value: The first operand.
        :type a_value: float
        :param b_value: The second operand.
        :type b_value: float
        :return: This context, for further chaining.
        :rtype: CalculatorFluentContext
        '''

        # Start a new expression with the '/' operator.
        return self._start(a.core.DIVIDE_OPERATOR, a_value, b_value)

    # * method: divide_by
    def divide_by(self, value: float) -> 'CalculatorFluentContext':
        '''
        Continue the active expression by dividing by one more operand.

        :param value: The operand to divide by next.
        :type value: float
        :return: This context, for further chaining.
        :rtype: CalculatorFluentContext
        '''

        # Continue the active expression with the '/' operator.
        return self._continue(a.core.DIVIDE_OPERATOR, value)

    # * method: run
    def run(self,
            feature_id: str = None,
            headers: Dict[str, str] = {},
            data: Dict[str, Any] = {},
            **kwargs) -> Any:
        '''
        Execute a feature -- or, when a fluent chain is active, resolve it.

        ``run()`` is fundamentally an agnostic executor; requiring
        ``feature_id`` is really a property of ``execute_feature``'s
        single-feature dispatch, not of ``run()`` itself. This override
        relaxes that requirement for exactly one case: once a fluent chain
        is active, every argument becomes irrelevant -- there's already
        exactly one thing left to run, ``calc.resolve`` -- so ``run()``
        finalizes the chain instead.

        When no chain is active, every argument (``feature_id`` included)
        passes straight through to the plain client unchanged. This is what
        lets a configured feature -- ``calc.history``, ``formula.save``, and
        so on -- keep working exactly as before via
        ``calc_app.run('calc.history', data={})``. Omitting ``feature_id``
        in that case isn't specially guarded against here; the framework's
        own feature lookup raises ``FEATURE_NOT_FOUND`` on its own, which is
        exactly the safeguard we want -- so is passing an explicit
        ``feature_id`` while a chain happens to be active: it's simply
        ignored, since resolving the active chain is the only thing left
        to do.

        :param feature_id: The feature to execute; required only when no
            fluent chain is active. Ignored once a chain is active.
        :type feature_id: str | None
        :param headers: The request headers. Ignored once a chain is active.
        :type headers: Dict[str, str]
        :param data: The request data. Ignored once a chain is active.
        :type data: Dict[str, Any]
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: The response of the executed feature, or the fully-reduced
            value of the finalized chain.
        :rtype: Any
        '''

        # No chain active: defer entirely to the plain client's run().
        if self._pending_request is None:
            return super().run(feature_id, headers, data, **kwargs)

        # A chain is active: resolve it in a single calc.resolve run, then
        # clear the active chain so the context is ready for a new one.
        value = super().run(a.core.CALC_RESOLVE_ID, data={})
        self._pending_request = None

        # Return the fully-reduced result.
        return value

    # * method: reset
    def reset(self) -> 'CalculatorFluentContext':
        '''
        Abandon the active chain, if any, without evaluating it.

        :return: This context, for further chaining.
        :rtype: CalculatorFluentContext
        '''

        # Drop the persistent request; nothing else was ever written anywhere.
        self._pending_request = None

        # Return self so the caller may keep chaining.
        return self

    # * attribute: pending
    @property
    def pending(self) -> str | None:
        '''
        Safely peek at the active chain without finalizing it.

        :return: The rendered infix expression, or None when no chain is active.
        :rtype: str | None
        '''

        # Return None when there is nothing pending.
        if self._pending_request is None:
            return None

        # Render the logged terms without mutating or finalizing them.
        values, operators = self._pending_request.terms
        return Expression(values=values, operators=operators).display()
