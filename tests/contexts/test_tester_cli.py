"""Tiferet Tester CLI Context Tests"""

# *** imports

# ** core
from pathlib import Path
from unittest.mock import Mock

# ** infra
import pytest

# ** app
from tiferet import use_tester
from tiferet.assets import TiferetAPIError
from tiferet.assets.tester_cli import (
    ADD_FIXTURE_EVT_ID,
    FIXTURE_ADD_ID,
    FIXTURE_GET_ID,
    GET_FIXTURE_EVT_ID,
    MODULE_RUN_ID,
)
from tiferet.contexts.app import AppSessionContext
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.core import BaseContext
from tiferet.contexts.feature import FEATURE_CACHE_PREFIX
from tiferet.contexts.request import RequestContext
from tiferet.contexts.tester_cli import TesterCliSessionContext
from tiferet.domain import AppSession, Feature
from tiferet.domain.tester_module import TestModuleAddress
from tiferet.events import DomainEvent
from tiferet.events.tester_module import WriteTestModuleDocument

# *** testers

# ** tester: test_tester_cli_session_context
@use_tester(
    type='context',
    target_cls=TesterCliSessionContext,
    domain_cls=AppSession,
    from_domain_cases=[
        {
            'data': {
                'id': 'tester_cli',
                'name': 'Tester CLI',
            },
            'kwargs': {
                'get_dependency': lambda *args, **kwargs: None,
            },
        },
    ],
    domain_type_cases=[
        {
            'declares': False,
        },
    ],
    for_domain_cases=[
        {
            'domain_module_path': 'tiferet.domain.app',
            'domain_class_name': 'AppSession',
            'context_module_path': 'tiferet.contexts.app',
            'context_class_name': 'AppSessionContext',
        },
    ],
)
class TestTesterCliSessionContext:
    '''
    Tests for TesterCliSessionContext.
    '''

    # * method: bind_session
    def bind_session(self, **handlers):
        '''
        Bind a tester CLI session with injected handlers.

        :param handlers: Handler and slot overrides for the session.
        :type handlers: dict
        :return: The bound tester CLI session context.
        :rtype: TesterCliSessionContext
        '''

        # Bind the tester CLI session to the catalog app session.
        return TesterCliSessionContext.from_domain(
            AppSession(id='tester_cli', name='Tester CLI'),
            get_dependency=handlers.get(
                'get_dependency',
                lambda *args, **kwargs: None,
            ),
            parse_cli_args=handlers.get('parse_cli_args'),
            cache=handlers.get('cache'),
            build_logger_handler=handlers.get('build_logger_handler'),
            execute_feature_handler=handlers.get(
                'execute_feature_handler',
                lambda *args, **kwargs: None,
            ),
            create_request_handler=handlers.get(
                'create_request_handler',
                lambda interface_id, feature_id, headers, data: RequestContext(
                    headers={**(headers or {}), 'interface_id': interface_id},
                    data=data,
                    feature_id=feature_id,
                    session_id=interface_id,
                ),
            ),
            raise_error_handler=handlers.get('raise_error_handler'),
            response_handler=handlers.get('response_handler'),
            run_test_module=handlers.get('run_test_module'),
            read_text=handlers.get('read_text'),
            replace_module=handlers.get('replace_module'),
            resolve_address=handlers.get('resolve_address'),
        )

    # * method: writer_address
    def writer_address(self) -> TestModuleAddress:
        '''
        Return the injected writer command address.

        :return: The test-module address.
        :rtype: TestModuleAddress
        '''

        # Return the unused domain/test_error address.
        return TestModuleAddress(
            rel='domain/test_error',
            base_dir='.',
            path='/unused/tiferet_tests/domain/test_error.yml',
        )

    # * method: seed_feature
    def seed_feature(self, cache: CacheContext, feature_id: str, service_id: str) -> None:
        '''
        Store one catalog feature on the cache.

        :param cache: The session cache.
        :type cache: CacheContext
        :param feature_id: The feature identifier.
        :type feature_id: str
        :param service_id: The first step service identifier.
        :type service_id: str
        :return: None
        :rtype: None
        '''

        # Store a one-step feature under the feature cache prefix.
        cache.set(
            feature_id,
            Feature(
                id=feature_id,
                name=feature_id,
                steps=[
                    {
                        'service_id': service_id,
                        'name': feature_id,
                    },
                ],
            ),
            *FEATURE_CACHE_PREFIX,
        )

    # * test: tester_cli_from_domain_binds_the_domain
    def test_tester_cli_from_domain_binds_the_domain(self, test_ctx) -> None:
        '''
        Assert from_domain binds TesterCliSessionContext to the AppSession.

        :param test_ctx: The bound context tester context.
        :type test_ctx: ContextTesterContext
        :return: None
        :rtype: None
        '''

        # Assert from_domain cases bind the target context and domain identity.
        test_ctx.assert_from_domain()

    # * test: tester_cli_omits_domain_type
    def test_tester_cli_omits_domain_type(self, test_ctx) -> None:
        '''
        Assert domain_type is not in the tester CLI session namespace.

        :param test_ctx: The bound context tester context.
        :type test_ctx: ContextTesterContext
        :return: None
        :rtype: None
        '''

        # Assert domain_type is omitted from TesterCliSessionContext.
        test_ctx.assert_domain_type()

    # * test: app_session_stays_app_session_context
    def test_app_session_stays_app_session_context(self, test_ctx) -> None:
        '''
        Assert BaseContext.for_domain still resolves AppSessionContext.

        :param test_ctx: The bound context tester context.
        :type test_ctx: ContextTesterContext
        :return: None
        :rtype: None
        '''

        # Assert the registry mapping for AppSession is unchanged.
        test_ctx.assert_for_domain()
        assert BaseContext.for_domain(AppSession) is AppSessionContext

    # * test: module_run_calls_the_injected_runner
    def test_module_run_calls_the_injected_runner(self) -> None:
        '''
        Assert module run calls the injected runner and returns its outcome.

        :return: None
        :rtype: None
        '''

        # Record the injected runner arguments.
        stored = {}

        def run_test_module(module_path, summary=False):
            stored['module_path'] = module_path
            stored['summary'] = summary
            return {
                'outcomes': [],
            }

        def parse_cli_args(argv):
            return (
                MODULE_RUN_ID,
                {},
                {
                    'module_path': 'tests/test_sample.py',
                    'summary': True,
                },
            )

        # Run module run through the injected runner.
        context = self.bind_session(
            parse_cli_args=parse_cli_args,
            run_test_module=run_test_module,
        )
        outcome = context.run(['module', 'run', 'tests/test_sample.py', '--summary'])

        # Assert the runner outcome and stored arguments.
        assert outcome == {
            'outcomes': [],
        }
        assert stored['module_path'] == 'tests/test_sample.py'
        assert stored['summary'] is True

    # * test: unwired_runner_raises
    def test_unwired_runner_raises(self) -> None:
        '''
        Assert an unwired module runner raises TiferetAPIError.

        :return: None
        :rtype: None
        '''

        # Run module run with a null runner.
        def parse_cli_args(argv):
            return MODULE_RUN_ID, {}, {'module_path': 'tests/test_sample.py'}

        context = self.bind_session(parse_cli_args=parse_cli_args)

        # Assert the unwired slot names the runner and the session.
        with pytest.raises(TiferetAPIError) as error:
            context.run(['module', 'run', 'tests/test_sample.py'])
        assert 'run_test_module' in str(error.value)
        assert 'tester_cli' in str(error.value)

    # * test: module_run_value_error_propagates
    def test_module_run_value_error_propagates(self) -> None:
        '''
        Assert a ValueError from the injected runner propagates.

        :return: None
        :rtype: None
        '''

        # Raise ValueError from the injected runner.
        def run_test_module(module_path, summary=False):
            raise ValueError('Not a Python test module: missing.')

        def parse_cli_args(argv):
            return MODULE_RUN_ID, {}, {'module_path': 'missing'}

        context = self.bind_session(
            parse_cli_args=parse_cli_args,
            run_test_module=run_test_module,
        )

        # Assert ValueError is not converted into an exit.
        with pytest.raises(ValueError) as error:
            context.run(['module', 'run', 'missing'])
        assert 'Not a Python test module: missing.' in str(error.value)

    # * test: writer_build_request_supplies_the_document
    def test_writer_build_request_supplies_the_document(self) -> None:
        '''
        Assert a writer command supplies the composed document on the request.

        :return: None
        :rtype: None
        '''

        # Inject a missing-file reader and a fixed address.
        address = self.writer_address()

        def resolve_address(rel, base_dir='.'):
            return address

        context = self.bind_session(
            read_text=lambda path: None,
            resolve_address=resolve_address,
        )

        # Run the writer command request build.
        request = context.build_request(
            FIXTURE_ADD_ID,
            data={
                'rel': 'domain/test_error',
                'payload': 'class_name: ErrorMessage',
            },
        )
        document = request.data['document']

        # Assert the document, fragment promotion, and create flag.
        assert request.data['working'] is document.body
        assert request.data['fragment'] == 'class_name: ErrorMessage'
        assert 'payload' not in request.data
        assert request._tester_create is True
        assert request._tester_address is address

    # * test: writer_set_data_strips_address_keys
    def test_writer_set_data_strips_address_keys(self) -> None:
        '''
        Assert the replaced set_data strips address keys and keeps the document.

        :return: None
        :rtype: None
        '''

        # Build the writer request, then replace its data.
        address = self.writer_address()

        def resolve_address(rel, base_dir='.'):
            return address

        context = self.bind_session(
            read_text=lambda path: None,
            resolve_address=resolve_address,
        )
        request = context.build_request(
            FIXTURE_ADD_ID,
            data={
                'rel': 'domain/test_error',
                'payload': 'class_name: ErrorMessage',
            },
        )
        document = request.data['document']
        request.set_data({
            'rel': 'domain/test_error',
            'name': 'error_message',
            'document': document,
        })

        # Assert rel is stripped and the document identity remains.
        assert 'rel' not in request.data
        assert request.data['name'] == 'error_message'
        assert request.data['document'] is document

    # * test: writer_execute_feature_replaces_the_file
    def test_writer_execute_feature_replaces_the_file(self) -> None:
        '''
        Assert a write step replaces the file and sets the path result.

        :return: None
        :rtype: None
        '''

        # Inject a missing-file reader and a null replace recorder.
        address = self.writer_address()
        replaced = {
            'path': None,
            'text': None,
            'create': None,
        }

        def resolve_address(rel, base_dir='.'):
            return address

        def replace_module(path, text, create=False):
            replaced['path'] = path
            replaced['text'] = text
            replaced['create'] = create

        cache = CacheContext()
        self.seed_feature(cache, FIXTURE_ADD_ID, ADD_FIXTURE_EVT_ID)
        context = self.bind_session(
            cache=cache,
            read_text=lambda path: None,
            replace_module=replace_module,
            resolve_address=resolve_address,
        )
        request = context.build_request(
            FIXTURE_ADD_ID,
            data={
                'rel': 'domain/test_error',
                'payload': 'class_name: ErrorMessage',
            },
        )

        # Run the writer command.
        outcome = context.execute_feature(FIXTURE_ADD_ID, request)
        written = DomainEvent.handle(
            WriteTestModuleDocument,
            document=request.data['document'],
            working=request.data['document'].body,
        )

        # Assert the file is replaced with the written document text.
        assert outcome is None
        assert request.result == '/unused/tiferet_tests/domain/test_error.yml'
        assert replaced['path'] == Path('/unused/tiferet_tests/domain/test_error.yml')
        assert replaced['create'] is True
        assert replaced['text'] == written.text

    # * test: query_execute_feature_does_not_replace_the_file
    def test_query_execute_feature_does_not_replace_the_file(self) -> None:
        '''
        Assert a query step leaves the file and does not set a result.

        :return: None
        :rtype: None
        '''

        # Inject a missing-file reader and a null replace recorder.
        address = self.writer_address()
        replaced = {
            'path': None,
            'text': None,
            'create': None,
        }

        def resolve_address(rel, base_dir='.'):
            return address

        def replace_module(path, text, create=False):
            replaced['path'] = path
            replaced['text'] = text
            replaced['create'] = create

        cache = CacheContext()
        self.seed_feature(cache, FIXTURE_GET_ID, GET_FIXTURE_EVT_ID)
        context = self.bind_session(
            cache=cache,
            read_text=lambda path: None,
            replace_module=replace_module,
            resolve_address=resolve_address,
        )
        request = context.build_request(
            FIXTURE_GET_ID,
            data={
                'rel': 'domain/test_error',
                'name': 'error_message',
            },
        )

        # Run the query command.
        outcome = context.execute_feature(FIXTURE_GET_ID, request)

        # Assert the file is left and the replace recorder stays null.
        assert outcome is None
        assert request.result is None
        assert replaced['path'] is None
        assert replaced['text'] is None
        assert replaced['create'] is None

    # * test: parse_failure_exits_2
    def test_parse_failure_exits_2(self) -> None:
        '''
        Assert a parse failure exits 2.

        :return: None
        :rtype: None
        '''

        # Raise during argv parse.
        def parse_cli_args(argv):
            raise Exception('bad argv')

        context = self.bind_session(parse_cli_args=parse_cli_args)

        # Assert the session exits 2.
        with pytest.raises(SystemExit) as error:
            context.run(['bad'])
        assert '2' in str(error.value)

    # * test: module_run_api_error_exits_1
    def test_module_run_api_error_exits_1(self) -> None:
        '''
        Assert a TiferetAPIError from the injected runner exits 1.

        :return: None
        :rtype: None
        '''

        # Raise TiferetAPIError from the injected runner.
        def run_test_module(module_path, summary=False):
            raise TiferetAPIError(
                error_code='TEST_MODULE_NOT_FOUND',
                message='TEST_MODULE_NOT_FOUND',
            )

        def parse_cli_args(argv):
            return MODULE_RUN_ID, {}, {'module_path': 'missing'}

        context = self.bind_session(
            parse_cli_args=parse_cli_args,
            run_test_module=run_test_module,
        )

        # Assert the module run exits 1.
        with pytest.raises(SystemExit) as error:
            context.run(['module', 'run', 'missing'])
        assert '1' in str(error.value)

    # * test: writer_command_api_error_exits_1
    def test_writer_command_api_error_exits_1(self) -> None:
        '''
        Assert a TiferetAPIError from the application session run exits 1.

        :return: None
        :rtype: None
        '''

        # Raise TiferetAPIError from the application session run.
        def parse_cli_args(argv):
            return (
                FIXTURE_GET_ID,
                {},
                {
                    'rel': 'domain/test_error',
                    'name': 'error_message',
                },
            )

        def execute_feature_handler(feature_id, request, **kwargs):
            raise TiferetAPIError(
                error_code='TEST_MODULE_NOT_FOUND',
                message='TEST_MODULE_NOT_FOUND',
            )

        address = self.writer_address()

        def resolve_address(rel, base_dir='.'):
            return address

        context = self.bind_session(
            parse_cli_args=parse_cli_args,
            execute_feature_handler=execute_feature_handler,
            build_logger_handler=lambda logger_id: Mock(),
            read_text=lambda path: None,
            resolve_address=resolve_address,
        )

        # Assert the writer command exits 1.
        with pytest.raises(SystemExit) as error:
            context.run(['fixture', 'get', 'domain/test_error', 'error_message'])
        assert '1' in str(error.value)
