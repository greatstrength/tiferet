"""Tiferet Tester CLI Context"""

# *** imports

# ** core
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List

# ** app
from .. import a
from ..assets import TiferetAPIError
from ..assets.tester_cli import (
    MODULE_RUN_ID,
    TESTER_WRITE_EVENT_REGISTRATIONS,
)
from ..events import DomainEvent
from ..events.tester_module import (
    ReadTestModuleDocument,
    WriteTestModuleDocument,
)
from .app import AppSessionContext, raise_unwired_handler_error
from .cli import CliSessionContext
from .feature import FEATURE_CACHE_PREFIX

# *** contexts

# ** context: tester_cli_session_context
class TesterCliSessionContext(CliSessionContext):
    '''
    The tester console session runs the catalog without a consumer config file.

    It omits domain_type so the application session stays registered to the
    application hub. The module-run id calls the injected runner. Every other
    command rides the application session run. This context supplies the
    document and writes the file after a write step.
    '''

    # * attribute: _run_test_module
    _run_test_module: Callable

    # * attribute: _read_text
    _read_text: Callable

    # * attribute: _replace_module
    _replace_module: Callable

    # * attribute: _resolve_address
    _resolve_address: Callable

    # * init
    def __init__(self,
            get_dependency: Callable,
            parse_cli_args: Callable = None,
            list_commands_handler: Callable = None,
            get_parent_args_handler: Callable = None,
            cache=None,
            build_logger_handler: Callable = None,
            execute_feature_handler: Callable = None,
            create_request_handler: Callable = None,
            raise_error_handler: Callable = None,
            response_handler: Callable = None,
            run_test_module: Callable = None,
            read_text: Callable = None,
            replace_module: Callable = None,
            resolve_address: Callable = None,
        ):
        '''
        Initialize the tester CLI session context.

        :param get_dependency: The injected service-resolution handler.
        :type get_dependency: Callable
        :param parse_cli_args: Injected callable that parses argv.
        :type parse_cli_args: Callable
        :param list_commands_handler: Injected zero-arg command lister.
        :type list_commands_handler: Callable
        :param get_parent_args_handler: Injected zero-arg parent-argument callable.
        :type get_parent_args_handler: Callable
        :param cache: The shared cache context.
        :type cache: CacheContext
        :param build_logger_handler: The logger-construction callable.
        :type build_logger_handler: Callable
        :param execute_feature_handler: The feature-execution callable.
        :type execute_feature_handler: Callable
        :param create_request_handler: The request-creation callable.
        :type create_request_handler: Callable
        :param raise_error_handler: The error-raising callable.
        :type raise_error_handler: Callable
        :param response_handler: The response-extraction callable.
        :type response_handler: Callable
        :param run_test_module: The injected module runner.
        :type run_test_module: Callable
        :param read_text: The injected module-text reader.
        :type read_text: Callable
        :param replace_module: The injected file-replace callable.
        :type replace_module: Callable
        :param resolve_address: The injected address resolver.
        :type resolve_address: Callable
        '''

        # Initialize the CLI session hub with its injected handlers.
        super().__init__(
            get_dependency=get_dependency,
            parse_cli_args=parse_cli_args,
            list_commands_handler=list_commands_handler,
            get_parent_args_handler=get_parent_args_handler,
            cache=cache,
            build_logger_handler=build_logger_handler,
            execute_feature_handler=execute_feature_handler,
            create_request_handler=create_request_handler,
            raise_error_handler=raise_error_handler,
            response_handler=response_handler,
        )

        # Store the injected runner, reader, replace, and address slots.
        self._run_test_module = run_test_module
        self._read_text = read_text
        self._replace_module = replace_module
        self._resolve_address = resolve_address

    # * method: build_request
    def build_request(self,
            feature_id: str,
            headers: Dict[str, str] = None,
            data: Dict[str, Any] = None,
        ):
        '''
        Build the request and supply the document a tester command expects.

        :param feature_id: The feature identifier.
        :type feature_id: str
        :param headers: The request headers.
        :type headers: Dict[str, str]
        :param data: The parsed command data.
        :type data: Dict[str, Any]
        :return: The request whose data is the document and the command arguments.
        :rtype: RequestContext
        '''

        # Build the request, then replace its data with the document.
        parsed = dict(data or {})
        request = super().build_request(feature_id, headers or {}, parsed)

        # Address keys and parse keys are not command arguments.
        arguments = {
            key: value
            for key, value in parsed.items()
            if key not in ('rel', 'base_dir', 'group', 'command')
        }
        payload = arguments.get('payload')
        if isinstance(payload, str) and not arguments.get('fragment'):
            arguments['fragment'] = arguments.pop('payload')

        # Resolve and read through the injected callables. Do not copy them.
        address = self._resolve_address(
            parsed.get('rel'),
            parsed.get('base_dir', '.'),
        )
        raw = self._read_text(address.path)
        document = DomainEvent.handle(
            ReadTestModuleDocument,
            address=address,
            text=raw,
        )

        # The schema still requires rel. The step must not receive it.
        # validate_request replaces data through set_data after coercion.
        request.set_data({
            'document': document,
            'working': document.body,
            'rel': parsed.get('rel'),
            **arguments,
        })

        def strip_address_keys(value):
            request.__class__.set_data(
                request,
                {
                    key: item
                    for key, item in value.items()
                    if key not in ('rel', 'base_dir', 'group', 'command')
                },
            )

        request.set_data = strip_address_keys
        request._tester_address = address
        request._tester_create = raw is None
        return request

    # * method: execute_feature
    def execute_feature(self, feature_id: str, request, **kwargs):
        '''
        Run the catalog step, then replace the file when the step is a write.

        :param feature_id: The feature identifier.
        :type feature_id: str
        :param request: The request context.
        :type request: RequestContext
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: None
        :rtype: None
        '''

        # The hub runs the existing step.
        super().execute_feature(feature_id, request, **kwargs)

        # A query leaves the file. A write serializes and replaces it.
        feature = self.cache.get(feature_id, *FEATURE_CACHE_PREFIX)
        step = feature.steps[0]
        if step.service_id not in TESTER_WRITE_EVENT_REGISTRATIONS:
            return
        document = request.data['document']
        written = DomainEvent.handle(
            WriteTestModuleDocument,
            document=document,
            working=document.body,
        )
        self._replace_module(
            Path(request._tester_address.path),
            written.text,
            create=request._tester_create,
        )
        request.set_result(request._tester_address.path)

    # * method: run
    def run(self, argv: List[str] = None, **kwargs) -> Any:
        '''
        Parse argv and run the catalog command.

        A parse failure exits 2. The module-run id calls the injected runner.
        Every other command rides the application session run.

        :param argv: Explicit argv list; defaults to sys.argv[1:] when None.
        :type argv: List[str]
        :param kwargs: Unused; present for signature compatibility.
        :type kwargs: dict
        :return: The runner report or the feature response.
        :rtype: Any
        '''

        # Parse argv. A parse failure is an argparse exit, not a domain error.
        try:
            feature_id, headers, data = self._parse_cli_args(argv)
        except Exception as error:
            print(error, file=sys.stderr)
            sys.exit(2)

        # The catalog module-run id calls the injected runner and returns.
        if feature_id == MODULE_RUN_ID:
            if self._run_test_module is None:
                raise_unwired_handler_error(
                    'run_test_module',
                    self.domain.id,
                )
            try:
                return self._run_test_module(
                    data.get('module_path'),
                    summary=bool(data.get('summary')),
                )
            except TiferetAPIError as error:
                print(error, file=sys.stderr)
                sys.exit(1)

        # Every other command rides the application session run.
        try:
            return AppSessionContext.run(
                self,
                feature_id,
                headers,
                data,
            )
        except TiferetAPIError as error:
            print(error, file=sys.stderr)
            sys.exit(1)
