# *** imports

# ** core
import uuid
from typing import Any, Callable, Dict

# ** app
from tiferet import TiferetError
from tiferet.contexts.app import AppSessionContext
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.request import RequestContext
from .. import assets as a
from .expression import ExpressionContext

# *** contexts

# ** context: calculator_app_context
class CalculatorAppContext(AppSessionContext):
    '''
    The fluent, user-facing calculator surface: a chainable, PEMDAS-aware
    client built on top of the app session hub. Every operator exposes two
    distinct methods -- a starter (two operands, begins a new expression)
    and a continuation (one operand, folds into the already-active
    expression) -- and every reduction dispatches through the real
    ``calc.*`` features, so validation, division-by-zero handling, and
    history recording all keep working unchanged.

    A fluent chain reuses the framework's own request infrastructure as its
    routing slip: the chain's identity *is* the ``session_id`` stamped onto
    every ``RequestContext`` built while it is active (see
    ``build_request``), and that same id keys the cached pending
    ``Expression`` in ``ExpressionContext``. No separate "expression id"
    concept is invented -- the request session_id is extended to carry that
    metaphorical role across the chain's calls.

    It intentionally omits ``domain_type`` so the ``ContextMeta`` registry
    keeps mapping ``AppSession`` to ``AppSessionContext``.
    '''

    # * attribute: session_id (private)
    _session_id: str | None

    # * init
    def __init__(self,
            get_dependency: Callable,
            cache: CacheContext = None,
            build_logger_handler: Callable = None,
            execute_feature_handler: Callable = None,
            create_request_handler: Callable = None,
            raise_error_handler: Callable = None,
            response_handler: Callable = None):
        '''
        Initialize the calculator app context.

        :param get_dependency: The DI resolution handler injected by the blueprint.
        :type get_dependency: Callable
        :param cache: The shared bootstrap cache.
        :type cache: CacheContext
        :param build_logger_handler: The logger-construction handler.
        :type build_logger_handler: Callable
        :param execute_feature_handler: The feature-execution handler.
        :type execute_feature_handler: Callable
        :param create_request_handler: The request-construction handler.
        :type create_request_handler: Callable
        :param raise_error_handler: The error-handling handler.
        :type raise_error_handler: Callable
        :param response_handler: The response-building handler.
        :type response_handler: Callable
        '''

        # Initialize the base application session hub.
        super().__init__(
            get_dependency=get_dependency,
            cache=cache,
            build_logger_handler=build_logger_handler,
            execute_feature_handler=execute_feature_handler,
            create_request_handler=create_request_handler,
            raise_error_handler=raise_error_handler,
            response_handler=response_handler,
        )

        # No expression is active until the first starter method is called.
        self._session_id = None

    # * method: build_request
    def build_request(self,
            feature_id: str,
            headers: Dict[str, str] = {},
            data: Dict[str, Any] = {}) -> RequestContext:
        '''
        Build the request context, stamping the active chain's session_id
        onto it when a fluent expression is in progress.

        Every ``self.run(...)`` call issued while a chain is active (each
        pairwise reduction, plus the caller's own calls like ``calc.history``)
        is correlated under the same ``session_id`` -- the request
        infrastructure's own routing slip, extended here to also key the
        chain's cached pending state.

        :param feature_id: The identifier of the feature to execute.
        :type feature_id: str
        :param headers: The request headers.
        :type headers: Dict[str, str]
        :param data: The request data.
        :type data: Dict[str, Any]
        :return: The constructed request context.
        :rtype: RequestContext
        '''

        # Build the request via the inherited hub, then stamp the active chain's session_id.
        request = super().build_request(feature_id, headers, data)
        if self._session_id is not None:
            request.session_id = self._session_id

        # Return the (possibly stamped) request context.
        return request

    # * method: _reduce (private)
    def _reduce(self, operator: str, left: float, right: float) -> Any:
        '''
        Compute a single pairwise reduction by dispatching through the real
        arithmetic feature configured for the given operator.

        :param operator: The operator symbol to reduce.
        :type operator: str
        :param left: The left operand.
        :type left: float
        :param right: The right operand.
        :type right: float
        :return: The result of the underlying feature execution.
        :rtype: Any
        '''

        # Dispatch through the existing calc.* feature for this operator.
        feature_id = a.calc.OPERATOR_FEATURE_MAP[operator]
        return self.run(feature_id, data=dict(a=left, b=right))

    # * method: _start (private)
    def _start(self, operator: str, first: float, second: float) -> 'CalculatorAppContext':
        '''
        Begin a brand-new expression from two operands.

        :param operator: The operator joining the two operands.
        :type operator: str
        :param first: The first (leading) operand.
        :type first: float
        :param second: The second operand.
        :type second: float
        :return: This context, for further chaining.
        :rtype: CalculatorAppContext
        '''

        # Refuse to clobber an already-active expression.
        self._guard(
            self._session_id is None,
            a.calc.EXPRESSION_ALREADY_ACTIVE_ID,
            session_id=self._session_id,
        )

        # Start a fresh, uniquely-identified chain and push the first term.
        self._session_id = uuid.uuid4().hex
        expression_context = ExpressionContext.load(self.cache, self._session_id)
        expression_context.start(first)
        expression_context.apply_term(operator, second, reduce=self._reduce)
        expression_context.save(self.cache)

        # Return self so the caller may keep chaining.
        return self

    # * method: _continue (private)
    def _continue(self, operator: str, operand: float) -> 'CalculatorAppContext':
        '''
        Fold one more operand into the already-active expression.

        :param operator: The operator joining the operand to the running expression.
        :type operator: str
        :param operand: The next operand.
        :type operand: float
        :return: This context, for further chaining.
        :rtype: CalculatorAppContext
        '''

        # Require an active expression to continue.
        self._guard(
            self._session_id is not None,
            a.calc.NO_ACTIVE_EXPRESSION_ID,
        )

        # Fold the operand into the active expression.
        expression_context = ExpressionContext.load(self.cache, self._session_id)
        expression_context.apply_term(operator, operand, reduce=self._reduce)
        expression_context.save(self.cache)

        # Return self so the caller may keep chaining.
        return self

    # * method: add
    def add(self, a_value: float, b_value: float) -> 'CalculatorAppContext':
        '''
        Begin a new expression by adding two operands.

        :param a_value: The first operand.
        :type a_value: float
        :param b_value: The second operand.
        :type b_value: float
        :return: This context, for further chaining.
        :rtype: CalculatorAppContext
        '''

        # Start a new expression with the '+' operator.
        return self._start(a.calc.ADD_OPERATOR, a_value, b_value)

    # * method: add_to
    def add_to(self, value: float) -> 'CalculatorAppContext':
        '''
        Continue the active expression by adding one more operand.

        :param value: The operand to add next.
        :type value: float
        :return: This context, for further chaining.
        :rtype: CalculatorAppContext
        '''

        # Continue the active expression with the '+' operator.
        return self._continue(a.calc.ADD_OPERATOR, value)

    # * method: subtract
    def subtract(self, a_value: float, b_value: float) -> 'CalculatorAppContext':
        '''
        Begin a new expression by subtracting the second operand from the first.

        :param a_value: The first operand.
        :type a_value: float
        :param b_value: The second operand.
        :type b_value: float
        :return: This context, for further chaining.
        :rtype: CalculatorAppContext
        '''

        # Start a new expression with the '-' operator.
        return self._start(a.calc.SUBTRACT_OPERATOR, a_value, b_value)

    # * method: subtract_from
    def subtract_from(self, value: float) -> 'CalculatorAppContext':
        '''
        Continue the active expression by subtracting one more operand.

        Despite the name, this appends "- value" to the running expression
        (continuing left-to-right) -- it does not compute "value - current".

        :param value: The operand to subtract next.
        :type value: float
        :return: This context, for further chaining.
        :rtype: CalculatorAppContext
        '''

        # Continue the active expression with the '-' operator.
        return self._continue(a.calc.SUBTRACT_OPERATOR, value)

    # * method: multiply
    def multiply(self, a_value: float, b_value: float) -> 'CalculatorAppContext':
        '''
        Begin a new expression by multiplying two operands.

        :param a_value: The first operand.
        :type a_value: float
        :param b_value: The second operand.
        :type b_value: float
        :return: This context, for further chaining.
        :rtype: CalculatorAppContext
        '''

        # Start a new expression with the '*' operator.
        return self._start(a.calc.MULTIPLY_OPERATOR, a_value, b_value)

    # * method: multiply_by
    def multiply_by(self, value: float) -> 'CalculatorAppContext':
        '''
        Continue the active expression by multiplying by one more operand.

        :param value: The operand to multiply by next.
        :type value: float
        :return: This context, for further chaining.
        :rtype: CalculatorAppContext
        '''

        # Continue the active expression with the '*' operator.
        return self._continue(a.calc.MULTIPLY_OPERATOR, value)

    # * method: divide
    def divide(self, a_value: float, b_value: float) -> 'CalculatorAppContext':
        '''
        Begin a new expression by dividing the first operand by the second.

        :param a_value: The first operand.
        :type a_value: float
        :param b_value: The second operand.
        :type b_value: float
        :return: This context, for further chaining.
        :rtype: CalculatorAppContext
        '''

        # Start a new expression with the '/' operator.
        return self._start(a.calc.DIVIDE_OPERATOR, a_value, b_value)

    # * method: divide_by
    def divide_by(self, value: float) -> 'CalculatorAppContext':
        '''
        Continue the active expression by dividing by one more operand.

        :param value: The operand to divide by next.
        :type value: float
        :return: This context, for further chaining.
        :rtype: CalculatorAppContext
        '''

        # Continue the active expression with the '/' operator.
        return self._continue(a.calc.DIVIDE_OPERATOR, value)

    # * attribute: result
    @property
    def result(self) -> Any:
        '''
        Finalize the active expression and return its fully-reduced value.

        Draining the expression discards its cache entry and clears the
        active expression id, so the context is immediately ready to start a
        new chain.

        :return: The fully-reduced numeric result.
        :rtype: Any
        '''

        # Require an active expression to finalize.
        self._guard(
            self._session_id is not None,
            a.calc.NO_ACTIVE_EXPRESSION_ID,
        )

        # Finalize the expression, then discard its cache entry and reset state.
        expression_context = ExpressionContext.load(self.cache, self._session_id)
        value = expression_context.finalize(reduce=self._reduce)
        expression_context.discard(self.cache)
        self._session_id = None

        # Return the fully-reduced result.
        return value

    # * method: reset
    def reset(self) -> 'CalculatorAppContext':
        '''
        Abandon the active expression, if any, without evaluating it.

        :return: This context, for further chaining.
        :rtype: CalculatorAppContext
        '''

        # Discard the active expression's cache entry, if one exists.
        if self._session_id is not None:
            ExpressionContext.load(self.cache, self._session_id).discard(self.cache)
            self._session_id = None

        # Return self so the caller may keep chaining.
        return self

    # * attribute: pending
    @property
    def pending(self) -> str | None:
        '''
        Safely peek at the active expression without finalizing it.

        :return: The rendered infix expression, or None when no expression is active.
        :rtype: str | None
        '''

        # Return None when there is nothing pending.
        if self._session_id is None:
            return None

        # Render the active expression without mutating or finalizing it.
        return ExpressionContext.load(self.cache, self._session_id).display()

    # * method: _guard (private)
    def _guard(self, expression: bool, error_code: str, **kwargs) -> None:
        '''
        Raise a structured TiferetError when a guard expression is falsy.

        :param expression: The guard expression to check.
        :type expression: bool
        :param error_code: The error code to raise when the expression is falsy.
        :type error_code: str
        :param kwargs: Additional error keyword arguments.
        :type kwargs: dict
        '''

        # Raise the structured error when the guard expression is falsy.
        if not expression:
            TiferetError.raise_error(error_code, **kwargs)
