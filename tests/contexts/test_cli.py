"""Tiferet CLI Context Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.assets import TiferetAPIError
from tiferet.domain import CliArgument, CliCommand
from tiferet.mappers import AppSessionAggregate
from tiferet.contexts.cli import (
    CliContext,
    CliRequestContext,
    CliSessionContext,
    build_cli_record,
    add_default_cli_commands,
    get_default_cli_commands,
)
from tiferet.contexts.app import AppSessionContext
from tiferet.contexts.cache import CacheContext
from tiferet.domain import CliRecord, CliOutputRecord, CliRecordList
from tiferet.blueprints.cli import (
    build_argument_parser as build_parser,
    derive_feature_request,
    group_commands_by_key,
)
from tiferet.contexts.request import RequestContext

# *** fixtures

# ** fixture: app_interface
@pytest.fixture
def app_interface():
    '''
    Fixture to create an AppSessionAggregate bound as the CLI context domain.

    :return: An AppSessionAggregate instance.
    :rtype: AppSessionAggregate
    '''

    # Create a test interface pointing at the CLI context.
    return AppSessionAggregate(
        id='test_cli',
        name='Test CLI',
        module_path='tiferet.contexts.cli',
        class_name='CliContext',
        description='The test CLI interface.',
        flags=['test'],
        services=[],
    )

# ** fixture: cli_context
@pytest.fixture
def cli_context(app_interface):
    '''
    Fixture to create a CliContext bound to the test interface with mock events.

    The CLI collaborators default to returning empty lists; individual tests
    override ``list_commands_evt`` / ``get_parent_args_evt`` return values.

    :return: A CliContext instance.
    :rtype: CliContext
    '''

    # Build mock CLI collaborators with empty defaults.
    list_commands_evt = mock.Mock()
    list_commands_evt.execute.return_value = []
    get_parent_args_evt = mock.Mock()
    get_parent_args_evt.execute.return_value = []

    # Construct the CLI context declaratively from the loaded interface.
    return CliContext.from_domain(
        app_interface,
        get_feature_evt=mock.Mock(),
        get_error_evt=mock.Mock(),
        logging_list_all_evt=mock.Mock(),
        get_dependency=mock.Mock(),
        list_commands_evt=list_commands_evt,
        get_parent_args_evt=get_parent_args_evt,
    )

# *** tests

# ** test: group_commands_by_key
def test_group_commands_by_key():
    '''
    Test that group_commands_by_key groups commands by group key in order.
    '''

    # Group a flat list of commands spanning two groups.
    commands = group_commands_by_key([
        CliCommand(name='Add', key='add', group_key='calc'),
        CliCommand(name='Subtract', key='subtract', group_key='calc'),
        CliCommand(name='Boot', key='boot', group_key='sys'),
    ])

    # Assert the commands are grouped by group key preserving order.
    assert set(commands.keys()) == {'calc', 'sys'}
    assert [c.key for c in commands['calc']] == ['add', 'subtract']
    assert [c.key for c in commands['sys']] == ['boot']

# ** test: derive_feature_request
def test_derive_feature_request():
    '''
    Test that derive_feature_request builds the feature id and headers,
    normalizing hyphens to underscores in the feature id only.
    '''

    # Derive from a parsed namespace with hyphenated group and command.
    feature_id, headers = derive_feature_request(
        {'group': 'my-calc', 'command': 'sub-tract', 'a': 1},
    )

    # Assert the feature id is normalized and headers keep raw values.
    assert feature_id == 'my_calc.sub_tract'
    assert headers == {'command_group': 'my-calc', 'command_key': 'sub-tract'}

# ** test: get_commands_groups_by_group_key
def test_get_commands_groups_by_group_key(cli_context):
    '''
    Test that get_commands groups commands by their group key in order.

    :param cli_context: The CliContext instance.
    :type cli_context: CliContext
    '''

    # Arrange the list-commands event to return commands across two groups.
    cli_context.list_commands_evt.execute.return_value = [
        CliCommand(name='Add', key='add', group_key='calc'),
        CliCommand(name='Subtract', key='subtract', group_key='calc'),
        CliCommand(name='Boot', key='boot', group_key='sys'),
    ]

    # Retrieve the grouped command map.
    commands = cli_context.get_commands()

    # Assert the commands are grouped by group key preserving order.
    assert set(commands.keys()) == {'calc', 'sys'}
    assert [c.key for c in commands['calc']] == ['add', 'subtract']
    assert [c.key for c in commands['sys']] == ['boot']

# ** test: get_commands_falls_back_to_default_commands
def test_get_commands_falls_back_to_default_commands(app_interface):
    '''
    Test that get_commands falls back to the context's bootstrap default command
    list when the repository (event) returns no commands.

    :param app_interface: The bound app interface.
    :type app_interface: AppSessionAggregate
    '''

    # Build a CLI context seeded with an id-keyed bootstrap default command.
    list_commands_evt = mock.Mock()
    list_commands_evt.execute.return_value = []
    context = CliContext.from_domain(
        app_interface,
        get_feature_evt=mock.Mock(),
        get_error_evt=mock.Mock(),
        logging_list_all_evt=mock.Mock(),
        get_dependency=mock.Mock(),
        list_commands_evt=list_commands_evt,
        get_parent_args_evt=mock.Mock(),
        default_commands={'sys.boot': {'name': 'Boot', 'key': 'boot', 'group_key': 'sys'}},
    )

    # Retrieve the commands; the empty event result falls back to the defaults.
    result = context.get_commands()

    # Assert the event was called with no default arguments and the bootstrap
    # default command was used as the fallback.
    list_commands_evt.execute.assert_called_once_with()
    assert set(result.keys()) == {'sys'}
    assert [c.key for c in result['sys']] == ['boot']

# ** test: build_parser_parses_command_arguments
def test_build_parser_parses_command_arguments():
    '''
    Test that build_parser produces a parser that parses command arguments.
    '''

    # Build a command map with a single typed command.
    commands = {
        'calc': [
            CliCommand(
                name='Add', key='add', group_key='calc',
                arguments=[
                    CliArgument(name_or_flags=['a'], type='int'),
                    CliArgument(name_or_flags=['b'], type='int'),
                ],
            ),
        ],
    }

    # Build the parser (no parent arguments) and parse a sample argv.
    parser = build_parser(commands, [])
    parsed = vars(parser.parse_args(['calc', 'add', '1', '2']))

    # Assert the group, command, and typed values parse correctly.
    assert parsed['group'] == 'calc'
    assert parsed['command'] == 'add'
    assert parsed['a'] == 1
    assert parsed['b'] == 2

# ** test: build_parser_merges_parent_args_and_skips_collisions
def test_build_parser_merges_parent_args_and_skips_collisions():
    '''
    Test that parent arguments are merged but colliding flags are skipped.
    '''

    # Arrange parent arguments including one that collides with the command arg.
    parent_arguments = [
        CliArgument(name_or_flags=['--verbose'], action='store_true'),
        CliArgument(name_or_flags=['a']),
    ]

    # Build a command map whose command declares a colliding 'a' argument.
    commands = {
        'calc': [
            CliCommand(
                name='Add', key='add', group_key='calc',
                arguments=[CliArgument(name_or_flags=['a'], type='int')],
            ),
        ],
    }

    # Build the parser and parse argv including the non-colliding parent flag.
    parser = build_parser(commands, parent_arguments)
    parsed = vars(parser.parse_args(['calc', 'add', '5', '--verbose']))

    # Assert the command arg parses and the parent flag is merged in.
    assert parsed['a'] == 5
    assert parsed['verbose'] is True

# ** test: parse_cli_request_builds_request
def test_parse_cli_request_builds_request(cli_context):
    '''
    Test that parse_cli_request derives feature id, headers, and data.

    :param cli_context: The CliContext instance.
    :type cli_context: CliContext
    '''

    # Arrange a single typed command.
    cli_context.list_commands_evt.execute.return_value = [
        CliCommand(
            name='Add', key='add', group_key='calc',
            arguments=[
                CliArgument(name_or_flags=['a'], type='int'),
                CliArgument(name_or_flags=['b'], type='int'),
            ],
        ),
    ]

    # Parse the CLI request.
    request = cli_context.parse_cli_request(['calc', 'add', '1', '2'])

    # Assert the request context carries the derived feature id, headers, and data.
    assert isinstance(request, RequestContext)
    assert request.feature_id == 'calc.add'
    assert request.headers['command_group'] == 'calc'
    assert request.headers['command_key'] == 'add'
    assert request.headers['interface_id'] == cli_context.domain.id
    assert request.data['a'] == 1
    assert request.data['b'] == 2

# ** test: parse_cli_request_normalizes_hyphens
def test_parse_cli_request_normalizes_hyphens(cli_context):
    '''
    Test that hyphenated group/command keys normalize to an underscore feature id.

    :param cli_context: The CliContext instance.
    :type cli_context: CliContext
    '''

    # Arrange a command with hyphenated group and key.
    cli_context.list_commands_evt.execute.return_value = [
        CliCommand(name='Subtract', key='sub-tract', group_key='my-calc'),
    ]

    # Parse the CLI request.
    request = cli_context.parse_cli_request(['my-calc', 'sub-tract'])

    # Assert the feature id normalizes hyphens while headers keep raw values.
    assert request.feature_id == 'my_calc.sub_tract'
    assert request.headers['command_group'] == 'my-calc'
    assert request.headers['command_key'] == 'sub-tract'

# ** test: run_cli_success_prints_and_returns
def test_run_cli_success_prints_and_returns(cli_context, capsys):
    '''
    Test that run_cli delegates to run, prints, and returns the response.

    :param cli_context: The CliContext instance.
    :type cli_context: CliContext
    :param capsys: The pytest stdout/stderr capture fixture.
    :type capsys: pytest.CaptureFixture
    '''

    # Arrange a single typed command and stub the inherited run.
    cli_context.list_commands_evt.execute.return_value = [
        CliCommand(
            name='Add', key='add', group_key='calc',
            arguments=[
                CliArgument(name_or_flags=['a'], type='int'),
                CliArgument(name_or_flags=['b'], type='int'),
            ],
        ),
    ]
    cli_context.run = mock.Mock(return_value='RESULT')

    # Run the CLI for a valid command.
    result = cli_context.run_cli(['calc', 'add', '1', '2'])

    # Assert the response is returned and printed.
    assert result == 'RESULT'
    assert 'RESULT' in capsys.readouterr().out

    # Assert the inherited run was delegated to with the parsed request data.
    call = cli_context.run.call_args
    assert call.kwargs['feature_id'] == 'calc.add'
    assert call.kwargs['headers']['command_group'] == 'calc'
    assert call.kwargs['headers']['command_key'] == 'add'
    assert call.kwargs['data']['a'] == 1
    assert call.kwargs['data']['b'] == 2

# ** test: run_cli_parser_failure_exits_2
def test_run_cli_parser_failure_exits_2(cli_context):
    '''
    Test that an invalid CLI invocation exits with code 2.

    :param cli_context: The CliContext instance.
    :type cli_context: CliContext
    '''

    # Arrange a known command group.
    cli_context.list_commands_evt.execute.return_value = [
        CliCommand(name='Add', key='add', group_key='calc'),
    ]

    # Run the CLI with an unknown group and assert an exit code of 2.
    with pytest.raises(SystemExit) as exc_info:
        cli_context.run_cli(['nonexistent-group'])
    assert exc_info.value.code == 2

# ** test: run_cli_api_error_exits_1
def test_run_cli_api_error_exits_1(cli_context):
    '''
    Test that a TiferetAPIError during execution exits with code 1.

    :param cli_context: The CliContext instance.
    :type cli_context: CliContext
    '''

    # Arrange a valid command and make the inherited run raise an API error.
    cli_context.list_commands_evt.execute.return_value = [
        CliCommand(
            name='Add', key='add', group_key='calc',
            arguments=[CliArgument(name_or_flags=['a'], type='int')],
        ),
    ]
    cli_context.run = mock.Mock(
        side_effect=TiferetAPIError(error_code='X', name='X Error', message='boom'),
    )

    # Run the CLI for a valid command and assert an exit code of 1.
    with pytest.raises(SystemExit) as exc_info:
        cli_context.run_cli(['calc', 'add', '1'])
    assert exc_info.value.code == 1


# *** build_cli_record

# ** test: build_cli_record_from_domain_object
def test_build_cli_record_from_domain_object() -> None:
    '''
    Test that build_cli_record extracts model_dump fields from a DomainObject,
    coercing all values to str.
    '''

    # Use a CliCommand as a representative DomainObject.
    command = CliCommand(name='Add', key='add', group_key='calc')

    # Build the record.
    record = build_cli_record(command)

    # Assert the record is a CliRecord with the expected field values.
    assert isinstance(record, CliRecord)
    assert record.fields['name'] == 'Add'
    assert record.fields['key'] == 'add'
    assert record.fields['group_key'] == 'calc'

# ** test: build_cli_record_omits_none_from_domain_object
def test_build_cli_record_omits_none_from_domain_object() -> None:
    '''
    Test that build_cli_record omits None-valued fields from a DomainObject.
    '''

    # Use a CliCommand with an explicit None description.
    command = CliCommand(name='Add', key='add', group_key='calc', description=None)

    # Build the record.
    record = build_cli_record(command)

    # Assert that the None-valued description is absent from the record fields.
    assert 'description' not in record.fields

# ** test: build_cli_record_from_dict
def test_build_cli_record_from_dict() -> None:
    '''
    Test that build_cli_record iterates a dict and coerces all values to str.
    '''

    # Build a record from a plain dict with a non-string value.
    record = build_cli_record({'name': 'Add', 'count': 42})

    # Assert the record has the expected fields with str values.
    assert isinstance(record, CliRecord)
    assert record.fields['name'] == 'Add'
    assert record.fields['count'] == '42'

# ** test: build_cli_record_from_primitive
def test_build_cli_record_from_primitive() -> None:
    '''
    Test that build_cli_record wraps a primitive in a single-field record
    keyed by "value".
    '''

    # Build a record from an integer primitive.
    record = build_cli_record(99)

    # Assert the record has a single "value" field coerced to str.
    assert isinstance(record, CliRecord)
    assert record.fields == {'value': '99'}


# *** CliRequestContext

# ** fixture: cli_request_context
@pytest.fixture
def cli_request_context() -> CliRequestContext:
    '''
    Fixture for a CliRequestContext with a None result.

    :return: A CliRequestContext instance.
    :rtype: CliRequestContext
    '''

    # Construct and return a basic CLI request context.
    return CliRequestContext(feature_id='test.feature')

# ** test: cli_request_context_handle_response_list
def test_cli_request_context_handle_response_list(
        cli_request_context: CliRequestContext,
) -> None:
    '''
    Test that handle_response converts a list result into a CliRecordList.

    :param cli_request_context: The CliRequestContext fixture.
    :type cli_request_context: CliRequestContext
    '''

    # Set the result to a list of domain objects.
    cli_request_context.result = [
        CliCommand(name='Add', key='add', group_key='calc'),
        CliCommand(name='Sub', key='sub', group_key='calc'),
    ]

    # Handle the response.
    output = cli_request_context.handle_response()

    # Assert a CliRecordList is returned with one record per item.
    assert isinstance(output, CliRecordList)
    assert len(output.records) == 2
    assert output.records[0].fields['name'] == 'Add'
    assert output.records[1].fields['name'] == 'Sub'

# ** test: cli_request_context_handle_response_domain_object
def test_cli_request_context_handle_response_domain_object(
        cli_request_context: CliRequestContext,
) -> None:
    '''
    Test that handle_response converts a DomainObject result into a CliOutputRecord.

    :param cli_request_context: The CliRequestContext fixture.
    :type cli_request_context: CliRequestContext
    '''

    # Set the result to a single domain object.
    cli_request_context.result = CliCommand(name='Add', key='add', group_key='calc')

    # Handle the response.
    output = cli_request_context.handle_response()

    # Assert a CliOutputRecord wrapping the serialised fields is returned.
    assert isinstance(output, CliOutputRecord)
    assert output.record.fields['name'] == 'Add'
    assert output.record.fields['key'] == 'add'

# ** test: cli_request_context_handle_response_dict
def test_cli_request_context_handle_response_dict(
        cli_request_context: CliRequestContext,
) -> None:
    '''
    Test that handle_response converts a dict result into a CliOutputRecord.

    :param cli_request_context: The CliRequestContext fixture.
    :type cli_request_context: CliRequestContext
    '''

    # Set the result to a plain dict.
    cli_request_context.result = {'id': 'calc.add', 'status': 'ok'}

    # Handle the response.
    output = cli_request_context.handle_response()

    # Assert a CliOutputRecord is returned with the dict fields.
    assert isinstance(output, CliOutputRecord)
    assert output.record.fields['id'] == 'calc.add'
    assert output.record.fields['status'] == 'ok'

# ** test: cli_request_context_handle_response_primitive
def test_cli_request_context_handle_response_primitive(
        cli_request_context: CliRequestContext,
) -> None:
    '''
    Test that handle_response passes primitives through unchanged.

    :param cli_request_context: The CliRequestContext fixture.
    :type cli_request_context: CliRequestContext
    '''

    # Set the result to a primitive string.
    cli_request_context.result = 'plain-string'

    # Handle the response.
    output = cli_request_context.handle_response()

    # Assert the primitive is returned as-is.
    assert output == 'plain-string'


# *** CliSessionContext

# ** fixture: cli_session_context
@pytest.fixture
def cli_session_context(app_interface):
    '''
    Fixture for a minimal CliSessionContext with no parse_cli_args injected
    (legacy-compatible mode) and a no-op response handler.

    :return: A CliSessionContext instance.
    :rtype: CliSessionContext
    '''

    # Build a CliSessionContext without a parse_cli_args closure.
    return CliSessionContext.from_domain(
        app_interface,
        logging_list_all_evt=mock.Mock(),
        get_dependency=mock.Mock(),
    )

# ** test: cli_session_context_build_response_prints_format_output
def test_cli_session_context_build_response_prints_format_output(
        cli_session_context: CliSessionContext,
        capsys,
) -> None:
    '''
    Test that build_response prints the formatted output when the request is a
    CliRequestContext and the model exposes format_output.

    :param cli_session_context: The CliSessionContext fixture.
    :type cli_session_context: CliSessionContext
    :param capsys: The pytest stdout/stderr capture fixture.
    :type capsys: pytest.CaptureFixture
    '''

    # Build a CliOutputRecord with known fields.
    output_record = CliOutputRecord(
        record=CliRecord(fields={'id': '42', 'name': 'Test'}),
    )

    # Wire the response handler to return the pre-built output record.
    cli_session_context._build_response = mock.Mock(return_value=output_record)

    # Call build_response with a CliRequestContext.
    request = CliRequestContext(feature_id='test.feature')
    result = cli_session_context.build_response(request)

    # Assert the formatted output was printed.
    out = capsys.readouterr().out
    assert 'id' in out
    assert '42' in out
    assert 'name' in out
    assert 'Test' in out

    # Assert the output record is returned.
    assert result is output_record

# ** test: cli_session_context_build_response_prints_primitive
def test_cli_session_context_build_response_prints_primitive(
        cli_session_context: CliSessionContext,
        capsys,
) -> None:
    '''
    Test that build_response prints the stringified model when the model has no
    format_output method and the request is a CliRequestContext.

    :param cli_session_context: The CliSessionContext fixture.
    :type cli_session_context: CliSessionContext
    :param capsys: The pytest stdout/stderr capture fixture.
    :type capsys: pytest.CaptureFixture
    '''

    # Wire the response handler to return a plain string.
    cli_session_context._build_response = mock.Mock(return_value='hello world')

    # Call build_response with a CliRequestContext.
    request = CliRequestContext(feature_id='test.feature')
    result = cli_session_context.build_response(request)

    # Assert the primitive was printed and returned.
    assert 'hello world' in capsys.readouterr().out
    assert result == 'hello world'

# ** test: cli_session_context_build_response_legacy_no_print
def test_cli_session_context_build_response_legacy_no_print(
        cli_session_context: CliSessionContext,
        capsys,
) -> None:
    '''
    Test that build_response does NOT print when the request is a plain
    RequestContext (legacy path), leaving printing to the caller.

    :param cli_session_context: The CliSessionContext fixture.
    :type cli_session_context: CliSessionContext
    :param capsys: The pytest stdout/stderr capture fixture.
    :type capsys: pytest.CaptureFixture
    '''

    # Wire the response handler to return a sentinel value.
    cli_session_context._build_response = mock.Mock(return_value='legacy-result')

    # Call build_response with a plain RequestContext (not CliRequestContext).
    request = RequestContext(feature_id='test.feature')
    result = cli_session_context.build_response(request)

    # Assert nothing was printed and the result was returned as-is.
    assert capsys.readouterr().out == ''
    assert result == 'legacy-result'

# ** test: cli_session_context_run_new_path
def test_cli_session_context_run_new_path(
        app_interface,
) -> None:
    '''
    Test that run(argv) in the new path calls the injected _parse_cli_args
    closure and delegates to super().run with the parsed request tuple.

    :param app_interface: The bound app interface fixture.
    :type app_interface: AppSessionAggregate
    '''

    # Build a parse closure that returns a known (feature_id, headers, data) tuple.
    parse_fn = mock.Mock(return_value=('calc.add', {'h': '1'}, {'a': 1}))

    # Build a CliSessionContext with parse_cli_args injected.
    context = CliSessionContext.from_domain(
        app_interface,
        logging_list_all_evt=mock.Mock(),
        get_dependency=mock.Mock(),
        parse_cli_args=parse_fn,
    )

    # Patch AppSessionContext.run to isolate CliSessionContext.run.
    with mock.patch.object(
        AppSessionContext, 'run', return_value='parsed-result',
    ) as mock_run:
        result = context.run(['calc', 'add', '1'])

    # Assert the parse closure was called with the provided argv.
    parse_fn.assert_called_once_with(['calc', 'add', '1'])

    # Assert super().run was dispatched with the parsed tuple.
    mock_run.assert_called_once_with('calc.add', headers={'h': '1'}, data={'a': 1})
    assert result == 'parsed-result'

# ** test: cli_session_context_run_legacy_path_feature_id_kwarg
def test_cli_session_context_run_legacy_path_feature_id_kwarg(
        cli_session_context: CliSessionContext,
) -> None:
    '''
    Test that run delegates to the parent when feature_id is passed as a kwarg
    (the pre-Phase-1 AppSessionContext.run calling convention).

    :param cli_session_context: The CliSessionContext fixture.
    :type cli_session_context: CliSessionContext
    '''

    # Patch AppSessionContext.run to verify the delegation.
    with mock.patch.object(
        AppSessionContext, 'run', return_value='legacy',
    ) as mock_run:
        result = cli_session_context.run(
            feature_id='calc.add', headers={'h': '1'}, data={'a': 1},
        )

    # Assert super().run was called with the forwarded kwargs.
    mock_run.assert_called_once_with(
        feature_id='calc.add', headers={'h': '1'}, data={'a': 1},
    )
    assert result == 'legacy'

# ** test: cli_session_context_run_legacy_path_no_parse_fn
def test_cli_session_context_run_legacy_path_no_parse_fn(
        cli_session_context: CliSessionContext,
) -> None:
    '''
    Test that run falls back to the parent when no _parse_cli_args is wired in,
    forwarding argv as feature_id so the call does not crash.

    :param cli_session_context: The CliSessionContext fixture.
    :type cli_session_context: CliSessionContext
    '''

    # Confirm no parse closure is wired (legacy-compatible context).
    assert cli_session_context._parse_cli_args is None

    # Patch AppSessionContext.run to verify delegation without a parse fn.
    with mock.patch.object(
        AppSessionContext, 'run', return_value='fallback',
    ) as mock_run:
        result = cli_session_context.run(feature_id='calc.add', headers={}, data={})

    # Assert the parent run was invoked and the result forwarded.
    mock_run.assert_called_once()
    assert result == 'fallback'


# *** add_default_cli_commands / get_default_cli_commands

# ** test: add_default_cli_commands_seeds_cache
def test_add_default_cli_commands_seeds_cache() -> None:
    '''
    Test that the add_default_cli_commands decorator pre-seeds the cache with
    typed CliCommand objects keyed by command id.
    '''

    # Define an id-keyed command catalog.
    commands = {
        'calc.add': {'name': 'Add', 'key': 'add', 'group_key': 'calc'},
        'calc.sub': {'name': 'Sub', 'key': 'sub', 'group_key': 'calc'},
    }

    # Wrap a bare cache-builder with the decorator.
    @add_default_cli_commands(commands)
    def build():
        return CacheContext()

    # Build the cache.
    cache = build()

    # Retrieve the seeded commands.
    result = get_default_cli_commands(cache)

    # Assert both commands are present as typed CliCommand objects.
    assert len(result) == 2
    ids = {cmd.id for cmd in result}
    assert 'calc.add' in ids
    assert 'calc.sub' in ids
    assert all(isinstance(cmd, CliCommand) for cmd in result)

# ** test: get_default_cli_commands_returns_empty_when_not_seeded
def test_get_default_cli_commands_returns_empty_when_not_seeded() -> None:
    '''
    Test that get_default_cli_commands returns an empty list when the cache has
    not been seeded with any CLI commands.
    '''

    # Build a bare (unseeded) cache.
    cache = CacheContext()

    # Assert no commands are returned.
    assert get_default_cli_commands(cache) == []
