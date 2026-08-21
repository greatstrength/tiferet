# *** imports

# ** core
from typing import Any, Callable

# ** app
from tiferet import TiferetError
from tiferet.contexts.app import AppSessionContext, raise_unwired_handler_error
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.request import RequestContext

# *** contexts

# ** context: calculator_app_context
class CalculatorAppContext(AppSessionContext):
    '''
    The calculator's own AppSessionContext: a plain, non-fluent client for
    the arithmetic bounded context, adding exactly one session-level
    orchestration concern on top of the inherited hub -- recording every
    successful run via ``record_run`` (see ``execute_feature``).

    It intentionally omits ``domain_type`` so the ``ContextMeta`` registry
    keeps mapping ``AppSession`` to ``AppSessionContext``.

    ``CalculatorFluentContext`` (``app/contexts/fluent.py``) extends this
    class with the chainable, PEMDAS-aware surface; this class carries none
    of that chaining machinery itself. The blueprint-composed ``resolver``
    is still exposed as an attribute (kept untyped here, since ``contexts``
    never imports ``di`` directly) so future collaborators can resolve
    additional services without a signature change.
    '''

    # * attribute: resolver
    resolver: Any

    # * attribute: record_run (private)
    _record_run: Callable

    # * init
    def __init__(self,
            get_dependency: Callable,
            cache: CacheContext = None,
            resolver: Any = None,
            build_logger_handler: Callable = None,
            execute_feature_handler: Callable = None,
            create_request_handler: Callable = None,
            raise_error_handler: Callable = None,
            response_handler: Callable = None,
            record_run_handler: Callable = None):
        '''
        Initialize the calculator app context.

        :param get_dependency: The DI resolution handler injected by the blueprint.
        :type get_dependency: Callable
        :param cache: The shared bootstrap cache.
        :type cache: CacheContext
        :param resolver: The blueprint-composed service resolver, exposed for
            any future DI-resolved collaborator; not required today since
            every reduction dispatches through the existing calc.* features.
        :type resolver: Any
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
        :param record_run_handler: The record-run handler, invoked once after
            every successful feature execution to persist run history at the
            session level rather than as a per-feature step.
        :type record_run_handler: Callable
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

        # Expose the resolver for any future DI-resolved collaborator.
        self.resolver = resolver

        # Store the record-run handler (validated lazily on first use).
        self._record_run = record_run_handler

    # * method: execute_feature
    def execute_feature(self, feature_id: str, request: RequestContext, **kwargs):
        '''
        Execute a feature, then record the completed run.

        Delegates execution to the inherited hub first; ``record_run`` only
        fires when that call succeeds, since an exception propagates before
        this line runs and is handled by ``AppSessionContext.run``'s existing
        ``except`` branch.

        :param feature_id: The identifier of the feature to execute.
        :type feature_id: str
        :param request: The request context object.
        :type request: RequestContext
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Execute the feature via the inherited hub.
        super().execute_feature(feature_id, request, **kwargs)

        # Record the completed run at the session level.
        self.record_run(feature_id, request)

    # * method: record_run
    def record_run(self, feature_id: str, request: RequestContext) -> None:
        '''
        Record a successfully completed feature run.

        Delegates to the injected handler; fails loudly via
        ``raise_unwired_handler_error`` when unwired, consistent with the
        base class's other template-method handlers.

        :param feature_id: The identifier of the feature that was executed.
        :type feature_id: str
        :param request: The request context object.
        :type request: RequestContext
        '''

        # Fail loudly when the record-run handler is unwired.
        if self._record_run is None:
            raise_unwired_handler_error(
                'record_run_handler',
                self.domain.id,
                feature_id=feature_id,
            )

        # Delegate to the injected record-run handler.
        self._record_run(feature_id, request)

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
