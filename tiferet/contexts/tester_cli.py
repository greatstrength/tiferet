"""Tiferet Tester CLI Context"""

# *** imports

# ** core
import json
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List

# ** app
from ..assets import TiferetAPIError, TiferetError
from ..assets.tester_cli import (
    MODULE_RUN_ID,
    TESTER_LOGGER_ID,
    TESTER_WRITE_EVENT_REGISTRATIONS,
)
from ..events import DomainEvent
from ..events.tester_module import ReadTestModuleDocument, WriteTestModuleDocument
from .app import AppSessionContext, raise_unwired_handler_error
from .cli import CliSessionContext
from .feature import FEATURE_CACHE_PREFIX

# *** contexts

# ** context: tester_cli_session_context
class TesterCliSessionContext(CliSessionContext):
    '''
    The tester console session runs the catalog without a consumer config file. It omits ``domain_type`` so the application session stays registered to the application hub. The module-run id calls the injected runner. Every other command rides the application session run. This context supplies the document and writes the file after a write step.
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
            resolve_address: Callable = None):
        '''
        Initialize the tester CLI session context.

        :param get_dependency: The DI resolution handler injected by the blueprint.
        :type get_dependency: Callable
        :param parse_cli_args: The injected callable that parses argv and returns
            a (feature_id, headers, data) tuple.
        :type parse_cli_args: Callable
        :param list_commands_handler: The injected zero-arg callable built by the
            CLI blueprint function of the same name.
        :type list_commands_handler: Callable
        :param get_parent_args_handler: The injected zero-arg callable built by the
            CLI blueprint function of the same name.
        :type get_parent_args_handler: Callable
        :param cache: The shared bootstrap cache.
        :type cache: Any
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
        :param run_test_module: The injected module runner. Null means unwired.
        :type run_test_module: Callable
        :param read_text: The injected module-text reader.
        :type read_text: Callable
        :param replace_module: The injected file-replace callable.
        :type replace_module: Callable
        :param resolve_address: The injected address resolver.
        :type resolve_address: Callable
        '''

        # Initialize the CLI session hub.
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

        # Store the injected tester CLI slots.
        self._run_test_module = run_test_module
        self._read_text = read_text
        self._replace_module = replace_module
        self._resolve_address = resolve_address

    # * method: build_request
    def build_request(self,
            feature_id: str,
            headers: Dict[str, str] = None,
            data: Dict[str, Any] = None):
        '''
        Build the request, then replace its data with the document a tester
        command expects.

        :param feature_id: The identifier of the feature to execute.
        :type feature_id: str
        :param headers: The request headers.
        :type headers: Dict[str, str]
        :param data: The parsed command data.
        :type data: Dict[str, Any]
        :return: The request carrying the composed document.
        :rtype: Any
        '''

        # Copy the parsed command data.
        parsed = dict(data or {})

        # Build the hub request from the parsed command data.
        request = super().build_request(
            feature_id,
            headers=headers or {},
            data=parsed,
        )

        # Keep command arguments that are not address or routing keys.
        arguments = {
            key: value
            for key, value in parsed.items()
            if key not in ('rel', 'base_dir', 'group', 'command')
        }

        # Promote a string payload to fragment when fragment is absent.
        if isinstance(arguments.get('payload'), str) and not arguments.get('fragment'):
            arguments['fragment'] = arguments.pop('payload')

        # Resolve the test-module address from the command data.
        address = self._resolve_address(
            parsed.get('rel'),
            base_dir=parsed.get('base_dir', '.'),
        )

        # Read the current module text. Null means the file is absent.
        raw = self._read_text(address.path)

        # Compose the document from the address and revision text.
        document = DomainEvent.handle(
            ReadTestModuleDocument,
            address=address,
            text=raw,
        )

        # Supply the document on the request. Keep rel for schema validation.
        request.set_data({
            'document': document,
            'working': document.body,
            'rel': parsed.get('rel'),
            **arguments,
        })

        # Strip address keys after validation. The step must not receive rel.
        def set_data(value):
            mapping = {
                key: item
                for key, item in value.items()
                if key not in ('rel', 'base_dir', 'group', 'command')
            }
            request.__class__.set_data(request, mapping)

        request.set_data = set_data

        # Record the address and whether this write creates the file.
        request._tester_address = address
        request._tester_create = raw is None

        # Return the request carrying the document.
        return request

    # * method: execute_feature
    def execute_feature(self, feature_id: str, request, **kwargs):
        '''
        Run the catalog step, then replace the file when the step is a write.

        :param feature_id: The identifier of the feature to execute.
        :type feature_id: str
        :param request: The request carrying the composed document.
        :type request: Any
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: Null.
        :rtype: None
        '''

        # Run the catalog step through the application session hub.
        super().execute_feature(feature_id, request, **kwargs)

        # Load the cached feature and inspect its first step.
        feature = self.cache.get(feature_id, *FEATURE_CACHE_PREFIX)
        step = feature.steps[0]

        # A query leaves the file. Only a write replaces it.
        if step.service_id not in TESTER_WRITE_EVENT_REGISTRATIONS:
            return

        # Serialize the working document after the write step.
        document = request.data['document']
        written = DomainEvent.handle(
            WriteTestModuleDocument,
            document=document,
            working=document.body,
        )

        # Replace the file. Create it when the original revision was absent.
        self._replace_module(
            Path(request._tester_address.path),
            written.text,
            create=request._tester_create,
        )

        # Return the written path as the request result.
        request.set_result(request._tester_address.path)

    # * method: run
    def run(self, argv: List[str] = None, **kwargs) -> Any:
        '''
        Parse argv and run the catalog command.

        A parse failure exits 2. The module-run id calls the injected runner.
        A failed case or a load failure exits 1 through the ``tester`` logger,
        which writes one ``ERROR`` record per failure. Every other command
        rides the application session run.

        :param argv: The argument list; defaults to sys.argv[1:] when None.
        :type argv: List[str]
        :param kwargs: Not used; present for signature compatibility.
        :type kwargs: dict
        :return: The module-run outcome or the feature response.
        :rtype: Any
        '''

        # Parse argv. A parse failure exits 2.
        try:
            feature_id, headers, data = self._parse_cli_args(argv)
        except Exception as e:
            print(e, file=sys.stderr)
            sys.exit(2)

        # Module run calls the injected runner and does not enter the hub run.
        if feature_id == MODULE_RUN_ID:
            if self._run_test_module is None:
                raise_unwired_handler_error('run_test_module', self.domain.id)

            # Build the tester logger before the run.
            logger = self._build_logger(TESTER_LOGGER_ID)
            module_path = data.get('module_path')

            # Run the module. A load failure is logged once and exits 1.
            try:
                result = self._run_test_module(
                    module_path,
                    summary=bool(data.get('summary')),
                )
            except TiferetAPIError as e:
                print(e, file=sys.stderr)
                sys.exit(1)
            except Exception as error:
                code = getattr(error, 'error_code', None) or type(error).__name__
                message = str(error)
                if isinstance(error, TiferetError):
                    message = json.loads(message).get('message') or message
                logger.error(f'Module run failed to load {module_path}: {code}: {message}')
                sys.exit(1)

            # Log one error record per failed case, then return the report.
            failures = result.get('failures', []) if isinstance(result, dict) else []
            for failure in failures:
                logger.error(f"{failure['node_id']} FAILED: {failure['message']}")
            return result

        # Every other command rides the application session run.
        try:
            return AppSessionContext.run(
                self,
                feature_id,
                headers=headers,
                data=data,
            )
        except TiferetAPIError as e:
            print(e, file=sys.stderr)
            sys.exit(1)
