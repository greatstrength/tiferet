"""Tiferet CLI Context Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.assets import TiferetAPIError
from tiferet.contexts.app import AppSessionContext
from tiferet.contexts.cache import CacheContext
from tiferet.contexts.cli import (
    CliRequestContext,
    CliSessionContext,
    add_default_cli_commands,
    get_default_cli_commands,
    build_cli_record,
    CLI_COMMAND_CACHE_PREFIX,
)
from tiferet.contexts.core import ContextMeta
from tiferet.contexts.request import RequestContext
from tiferet.domain import (
    AppSession,
    CliCommand,
    CliRecord,
    CliOutputRecord,
    CliRecordList,
)

# *** fixtures

# ** fixture: app_session
@pytest.fixture
def app_session() -> AppSession:
    '''
    Fixture providing the app session bound as the CLI context domain object.

    :return: An AppSession instance.
    :rtype: AppSession
    '''

    # Return a test session pointing at the CLI context.
    return AppSession(
        id='test_cli',
        name='Test CLI',
        description='The test CLI interface.',
        flags=['test'],
        services=[],
    )

# ** fixture: cli_request_context
@pytest.fixture
def cli_request_context() -> CliRequestContext:
    '''
    Fixture providing a CLI request context with no result set.

    :return: A CliRequestContext instance.
    :rtype: CliRequestContext
    '''

    # Return a basic CLI request context.
    return CliRequestContext(feature_id='test.feature')

# ** fixture: cli_session_context
@pytest.fixture
def cli_session_context(app_session: AppSession) -> CliSessionContext:
    '''
    Fixture providing a CLI session context with no parsing callable injected.

    :param app_session: The bound app session fixture.
    :type app_session: AppSession
    :return: A CliSessionContext instance.
    :rtype: CliSessionContext
    '''

    # Return a CLI session context built without a parsing callable.
    return CliSessionContext.from_domain(
        app_session,
        get_dependency=mock.Mock(),
    )

# *** tests

# ** test: cli_record_fields
def test_cli_record_fields():
    '''
    Verify CliRecord stores its ordered attribute-to-value mapping.

    :return: None
    :rtype: None
    '''

    # Build a record with a single field.
    record = CliRecord(fields={'a': '1'})

    # Verify the field mapping is stored as supplied.
    assert record.fields == {'a': '1'}

# ** test: cli_output_record_format
def test_cli_output_record_format():
    '''
    Verify CliOutputRecord.format_output renders one padded attribute-value
    line per field, and an empty string when the record has no fields.

    :return: None
    :rtype: None
    '''

    # Build an output record with attribute names of differing widths.
    output = CliOutputRecord(
        record=CliRecord(fields={'id': 'calc.add', 'name': 'Add'}),
    )

    # Verify each field renders on its own line, padded to the widest name.
    assert output.format_output().split('\n') == [
        '  id  : calc.add',
        '  name: Add',
    ]

    # Verify an empty record renders as an empty string.
    assert CliOutputRecord(record=CliRecord()).format_output() == ''

# ** test: cli_record_list_format
def test_cli_record_list_format():
    '''
    Verify CliRecordList.format_output renders an aligned table with a header
    and separator row, and an empty string when there are no records.

    :return: None
    :rtype: None
    '''

    # Build a record list with two rows sharing the same columns.
    record_list = CliRecordList(records=[
        CliRecord(fields={'key': 'add', 'name': 'Add'}),
        CliRecord(fields={'key': 'subtract', 'name': 'Sub'}),
    ])

    # Verify the header, separator, and data rows align to the widest value.
    assert record_list.format_output().split('\n') == [
        'key       name',
        '--------  ----',
        'add       Add ',
        'subtract  Sub ',
    ]

    # Verify an empty record list renders as an empty string.
    assert CliRecordList().format_output() == ''

# ** test: build_cli_record_domain_object
def test_build_cli_record_domain_object():
    '''
    Verify build_cli_record serialises a DomainObject via model_dump, coercing
    values to str and omitting None-valued fields.

    :return: None
    :rtype: None
    '''

    # Build a record from a domain object with an explicit None description.
    record = build_cli_record(
        CliCommand(name='Add', key='add', group_key='calc', description=None),
    )

    # Verify the populated fields are coerced to str.
    assert isinstance(record, CliRecord)
    assert record.fields['name'] == 'Add'
    assert record.fields['key'] == 'add'
    assert record.fields['group_key'] == 'calc'

    # Verify the None-valued field is omitted.
    assert 'description' not in record.fields

# ** test: build_cli_record_dict
def test_build_cli_record_dict():
    '''
    Verify build_cli_record iterates a dict and coerces every value to str.

    :return: None
    :rtype: None
    '''

    # Build a record from a dict carrying a non-string value.
    record = build_cli_record({'name': 'Add', 'count': 42})

    # Verify each value is coerced to str.
    assert isinstance(record, CliRecord)
    assert record.fields == {'name': 'Add', 'count': '42'}

# ** test: build_cli_record_primitive
def test_build_cli_record_primitive():
    '''
    Verify build_cli_record wraps a primitive in a single "value" field.

    :return: None
    :rtype: None
    '''

    # Build a record from an integer primitive.
    record = build_cli_record(99)

    # Verify the primitive is wrapped under the "value" key.
    assert isinstance(record, CliRecord)
    assert record.fields == {'value': '99'}

# ** test: add_default_cli_commands
def test_add_default_cli_commands():
    '''
    Verify the add_default_cli_commands decorator seeds typed CliCommand
    objects under the CLI command cache prefix, keyed by command id.

    :return: None
    :rtype: None
    '''

    # Define an id-keyed command catalog.
    commands = {
        'calc.add': {'name': 'Add', 'key': 'add', 'group_key': 'calc'},
        'calc.sub': {'name': 'Sub', 'key': 'sub', 'group_key': 'calc'},
    }

    # Wrap a bare cache-builder with the decorator and build the cache.
    @add_default_cli_commands(commands)
    def build_cache() -> CacheContext:
        return CacheContext()

    cache = build_cache()

    # Verify the commands are seeded under the CLI command namespace.
    assert set(cache.get_by_prefix(*CLI_COMMAND_CACHE_PREFIX)) == {'calc.add', 'calc.sub'}

    # Verify the getter returns them as typed domain objects with their ids.
    result = get_default_cli_commands(cache)
    assert all(isinstance(command, CliCommand) for command in result)
    assert {command.id for command in result} == {'calc.add', 'calc.sub'}

# ** test: get_default_cli_commands_unseeded
def test_get_default_cli_commands_unseeded():
    '''
    Verify get_default_cli_commands returns an empty list when the cache has
    not been seeded with any CLI commands.

    :return: None
    :rtype: None
    '''

    # Verify an unseeded cache yields no commands.
    assert get_default_cli_commands(CacheContext()) == []

# ** test: cli_request_context_handle_response_list
def test_cli_request_context_handle_response_list(cli_request_context: CliRequestContext):
    '''
    Verify handle_response converts a list result into a CliRecordList.

    :param cli_request_context: The CLI request context fixture.
    :type cli_request_context: CliRequestContext
    :return: None
    :rtype: None
    '''

    # Set the result to a list of domain objects.
    cli_request_context.result = [
        CliCommand(name='Add', key='add', group_key='calc'),
        CliCommand(name='Sub', key='sub', group_key='calc'),
    ]

    # Handle the response.
    output = cli_request_context.handle_response()

    # Verify a CliRecordList is returned with one record per item.
    assert isinstance(output, CliRecordList)
    assert [record.fields['name'] for record in output.records] == ['Add', 'Sub']

# ** test: cli_request_context_handle_response_single
def test_cli_request_context_handle_response_single(cli_request_context: CliRequestContext):
    '''
    Verify handle_response converts a dict or DomainObject result into a
    CliOutputRecord.

    :param cli_request_context: The CLI request context fixture.
    :type cli_request_context: CliRequestContext
    :return: None
    :rtype: None
    '''

    # Set the result to a plain dict.
    cli_request_context.result = {'id': 'calc.add', 'status': 'ok'}

    # Verify a dict result becomes a CliOutputRecord.
    output = cli_request_context.handle_response()
    assert isinstance(output, CliOutputRecord)
    assert output.record.fields == {'id': 'calc.add', 'status': 'ok'}

    # Verify a DomainObject result also becomes a CliOutputRecord.
    cli_request_context.result = CliCommand(name='Add', key='add', group_key='calc')
    output = cli_request_context.handle_response()
    assert isinstance(output, CliOutputRecord)
    assert output.record.fields['name'] == 'Add'

# ** test: cli_request_context_handle_response_primitive
def test_cli_request_context_handle_response_primitive(cli_request_context: CliRequestContext):
    '''
    Verify handle_response passes a primitive result through unchanged.

    :param cli_request_context: The CLI request context fixture.
    :type cli_request_context: CliRequestContext
    :return: None
    :rtype: None
    '''

    # Set the result to a primitive string.
    cli_request_context.result = 'plain-string'

    # Verify the primitive is returned as-is.
    assert cli_request_context.handle_response() == 'plain-string'

# ** test: cli_session_context_not_registered
def test_cli_session_context_not_registered():
    '''
    Verify CliSessionContext declares no domain_type and so does not displace
    AppSessionContext in the ContextMeta registry.

    :return: None
    :rtype: None
    '''

    # Verify the CLI session context is absent from the registry.
    assert CliSessionContext not in ContextMeta.registry.values()

    # Verify AppSession still resolves to the base application session hub.
    assert ContextMeta.registry[AppSession] is AppSessionContext

# ** test: cli_session_context_build_response_formats
def test_cli_session_context_build_response_formats(
        cli_session_context: CliSessionContext,
        capsys,
):
    '''
    Verify build_response prints the formatted output for a CLI request whose
    model exposes format_output, and the stringified model when it does not.

    :param cli_session_context: The CLI session context fixture.
    :type cli_session_context: CliSessionContext
    :param capsys: The pytest stdout/stderr capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # Wire the response handler to return a formattable output record.
    output_record = CliOutputRecord(record=CliRecord(fields={'id': '42'}))
    cli_session_context._build_response = mock.Mock(return_value=output_record)

    # Verify the formatted output is printed and the model returned.
    result = cli_session_context.build_response(CliRequestContext(feature_id='test.feature'))
    assert capsys.readouterr().out.strip() == 'id: 42'
    assert result is output_record

    # Wire the response handler to return a plain string instead.
    cli_session_context._build_response = mock.Mock(return_value='hello world')

    # Verify the stringified model is printed and returned.
    result = cli_session_context.build_response(CliRequestContext(feature_id='test.feature'))
    assert capsys.readouterr().out.strip() == 'hello world'
    assert result == 'hello world'

# ** test: cli_session_context_build_response_legacy_no_print
def test_cli_session_context_build_response_legacy_no_print(
        cli_session_context: CliSessionContext,
        capsys,
):
    '''
    Verify build_response does not print for a plain RequestContext, leaving
    output to the caller on the legacy path.

    :param cli_session_context: The CLI session context fixture.
    :type cli_session_context: CliSessionContext
    :param capsys: The pytest stdout/stderr capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # Wire the response handler to return a sentinel value.
    cli_session_context._build_response = mock.Mock(return_value='legacy-result')

    # Build the response from a plain request context.
    result = cli_session_context.build_response(RequestContext(feature_id='test.feature'))

    # Verify nothing was printed and the value passed through.
    assert capsys.readouterr().out == ''
    assert result == 'legacy-result'

# ** test: cli_session_context_run_success
def test_cli_session_context_run_success(app_session: AppSession):
    '''
    Verify run parses argv via the injected callable and dispatches the parsed
    tuple through the inherited application session run.

    :param app_session: The bound app session fixture.
    :type app_session: AppSession
    :return: None
    :rtype: None
    '''

    # Build a parsing callable returning a known request tuple.
    parse_cli_args = mock.Mock(return_value=('calc.add', {'h': '1'}, {'a': 1}))

    # Build a CLI session context with the parsing callable injected.
    context = CliSessionContext.from_domain(
        app_session,
        get_dependency=mock.Mock(),
        parse_cli_args=parse_cli_args,
    )

    # Run the context with the inherited run patched out.
    with mock.patch.object(AppSessionContext, 'run', return_value='parsed-result') as run:
        result = context.run(['calc', 'add', '1'])

    # Verify the parsing callable received the supplied argv.
    parse_cli_args.assert_called_once_with(['calc', 'add', '1'])

    # Verify the parsed tuple was dispatched and its result returned.
    run.assert_called_once_with('calc.add', headers={'h': '1'}, data={'a': 1})
    assert result == 'parsed-result'

# ** test: cli_session_context_run_parse_error
def test_cli_session_context_run_parse_error(app_session: AppSession, capsys):
    '''
    Verify a parse failure is reported on stderr and exits with code 2.

    :param app_session: The bound app session fixture.
    :type app_session: AppSession
    :param capsys: The pytest stdout/stderr capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # Build a parsing callable that fails.
    parse_cli_args = mock.Mock(side_effect=SystemError('bad argv'))

    # Build a CLI session context with the failing parsing callable injected.
    context = CliSessionContext.from_domain(
        app_session,
        get_dependency=mock.Mock(),
        parse_cli_args=parse_cli_args,
    )

    # Verify the run exits with the argparse failure code.
    with pytest.raises(SystemExit) as exc_info:
        context.run(['bogus'])
    assert exc_info.value.code == 2

    # Verify the failure was reported on stderr.
    assert 'bad argv' in capsys.readouterr().err

# ** test: cli_session_context_run_api_error
def test_cli_session_context_run_api_error(app_session: AppSession, capsys):
    '''
    Verify a TiferetAPIError raised during dispatch is reported on stderr and
    exits with code 1.

    :param app_session: The bound app session fixture.
    :type app_session: AppSession
    :param capsys: The pytest stdout/stderr capture fixture.
    :type capsys: pytest.CaptureFixture
    :return: None
    :rtype: None
    '''

    # Build a CLI session context with a successful parsing callable.
    context = CliSessionContext.from_domain(
        app_session,
        get_dependency=mock.Mock(),
        parse_cli_args=mock.Mock(return_value=('calc.add', {}, {})),
    )

    # Build the structured API error raised by the inherited run.
    api_error = TiferetAPIError(
        error_code='FEATURE_NOT_FOUND',
        name='FEATURE_NOT_FOUND',
        message='Feature not found: calc.add.',
    )

    # Verify the run exits with the API error code.
    with mock.patch.object(AppSessionContext, 'run', side_effect=api_error):
        with pytest.raises(SystemExit) as exc_info:
            context.run(['calc', 'add'])
    assert exc_info.value.code == 1

    # Verify the error was reported on stderr.
    assert 'FEATURE_NOT_FOUND' in capsys.readouterr().err
