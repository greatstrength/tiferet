"""Tiferet Tester CLI Context"""

# *** imports

# ** core
import sys
from pathlib import Path
from typing import Any, Callable, List

# ** app
from .. import a
from ..assets import TiferetAPIError, TiferetError
from ..assets.tester import TEST_MODULE_LOAD_FAILED_ID
from ..assets.tester_cli import (
    MODULE_RUN_ID,
    TESTER_WRITE_EVENT_REGISTRATIONS,
)
from ..events import DomainEvent
from ..events.tester_module import (
    ReadTestModuleDocument,
    WriteTestModuleDocument,
)
from .app import raise_unwired_handler_error
from .cli import CliSessionContext
from .feature import FEATURE_CACHE_PREFIX

# *** contexts

# ** context: tester_cli_session_context
class TesterCliSessionContext(CliSessionContext):
    '''
    The tester console session runs the catalog without a consumer config file.

    It omits domain_type so the application session stays registered to the
    application hub. The module-run id calls the injected runner. A writer
    command runs the existing catalog step and supplies the document.
    '''

    # * attribute: _run_test_module
    _run_test_module: Callable

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

        # Store the injected module runner. An absent slot fails at the call.
        self._run_test_module = run_test_module

    # * method: run
    def run(self, argv: List[str] = None, **kwargs) -> Any:
        '''
        Parse argv and run the catalog command.

        A parse failure exits 2. The module-run id calls the injected runner.
        A writer command reads the one catalog step, supplies the document,
        and does not enter the inherited hub.

        :param argv: Explicit argv list; defaults to sys.argv[1:] when None.
        :type argv: List[str]
        :param kwargs: Unused; present for signature compatibility.
        :type kwargs: dict
        :return: The runner report, the verb result, or the written path.
        :rtype: Any
        '''

        # Parse argv. A parse failure is an argparse exit, not a domain error.
        try:
            feature_id, _headers, data = self._parse_cli_args(argv)
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

        # Read the one catalog step. Its class is the registered event.
        feature = self.cache.get(feature_id, *FEATURE_CACHE_PREFIX)
        step = feature.steps[0]
        registration = self.cache.get(
            step.service_id,
            *a.app.APP_SERVICE_CACHE_PREFIX,
        )
        event_cls = registration.get_service_type()

        # Pull the injected address and replace callables. Do not call them yet.
        resolve_address = data.get('resolve_address')
        replace_module = data.get('replace_module')
        base_dir = data.get('base_dir')
        rel = data.get('rel')
        arguments = {
            key: value
            for key, value in data.items()
            if key not in (
                'resolve_address',
                'replace_module',
                'base_dir',
                'rel',
            )
        }

        # A string payload with no fragment is the verb's fragment.
        payload = arguments.get('payload')
        if isinstance(payload, str) and not arguments.get('fragment'):
            arguments['fragment'] = arguments.pop('payload')

        # Read bytes the way the writer does. A missing file is None.
        def read_revision(path: str):
            '''Read module bytes. A missing file is None and is not created.'''

            file = Path(path)
            if not file.is_file():
                return None

            # A present file is read as bytes. It is not created.
            try:
                raw_bytes = file.read_bytes()
            except OSError as error:
                TiferetError.raise_error(
                    TEST_MODULE_LOAD_FAILED_ID,
                    f'Failed to read the test module: {error}.',
                    path=path,
                )

            # The revision is utf-8. A bad encoding is a load failure.
            try:
                return raw_bytes.decode('utf-8')
            except UnicodeDecodeError:
                TiferetError.raise_error(
                    TEST_MODULE_LOAD_FAILED_ID,
                    'A test module must be utf-8.',
                    path=path,
                )

        # Address, read, and the verb share one domain-error exit.
        try:
            address = resolve_address(rel, base_dir)
            raw = read_revision(address.path)
            document = DomainEvent.handle(
                ReadTestModuleDocument,
                address=address,
                text=raw,
            )
            result = DomainEvent.handle(
                event_cls,
                document=document,
                working=document.body,
                **arguments,
            )

            # A query leaves the file. A write serializes and replaces it.
            if step.service_id not in TESTER_WRITE_EVENT_REGISTRATIONS:
                return result
            written = DomainEvent.handle(
                WriteTestModuleDocument,
                document=document,
                working=document.body,
            )
            replace_module(
                Path(address.path),
                written.text,
                create=raw is None,
            )
            return address.path
        except TiferetError as error:
            print(
                TiferetAPIError(
                    error.error_code,
                    message=str(error),
                ),
                file=sys.stderr,
            )
            sys.exit(1)
