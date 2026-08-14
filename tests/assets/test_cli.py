"""Tests for CLI Assets — admin catalog reconciliation."""

# *** imports

# ** app
from tiferet.assets import cli as cli_assets

# *** constants

# ** constant: dict_typed_argument_specs
# (command_data attribute name, flag name) pairs that must use type='dict'.
DICT_TYPED_ARGUMENT_SPECS = [
    ('APP_ADD_CLI_CMD_DATA', '--constants'),
    ('APP_SET_CONSTANTS_CLI_CMD_DATA', '--constants'),
    ('APP_SET_SERVICE_CLI_CMD_DATA', '--parameters'),
    ('FEATURE_ADD_STEP_CLI_CMD_DATA', '--parameters'),
    ('SERVICE_ADD_CLI_CMD_DATA', '--parameters'),
    ('SERVICE_SET_DEFAULT_CLI_CMD_DATA', '--parameters'),
    ('SERVICE_SET_DEPENDENCY_CLI_CMD_DATA', '--parameters'),
    ('SERVICE_SET_CONSTANTS_CLI_CMD_DATA', '--constants'),
]

# *** functions

# ** function: find_argument
def find_argument(command_data: dict, flag: str) -> dict | None:
    '''
    Return the argument dict whose name_or_flags includes the given flag.

    :param command_data: A CLI command data dict with an arguments list.
    :type command_data: dict
    :param flag: The flag string to locate (e.g. '--constants').
    :type flag: str
    :return: The matching argument dict, or None when absent.
    :rtype: dict | None
    '''

    # Scan the command's arguments for the requested flag.
    for argument in command_data.get('arguments', []):
        if flag in argument.get('name_or_flags', []):
            return argument

    # Return None when the flag is not present.
    return None

# *** tests

# ** test: eight_flat_map_arguments_use_dict_type
def test_eight_flat_map_arguments_use_dict_type():
    '''
    Verify each of the eight flat-map admin CLI arguments uses type='dict'.
    '''

    # Assert every listed argument is typed as dict.
    for attr_name, flag in DICT_TYPED_ARGUMENT_SPECS:
        command_data = getattr(cli_assets, attr_name)
        argument = find_argument(command_data, flag)
        assert argument is not None, f'{attr_name} missing {flag}'
        assert argument['type'] == 'dict', f'{attr_name} {flag} type is {argument.get("type")!r}'

# ** test: error_add_includes_additional_messages_dict_arg
def test_error_add_includes_additional_messages_dict_arg():
    '''
    Verify error.add exposes --additional-messages with type='dict'.
    '''

    # Locate the additional-messages argument on error.add.
    argument = find_argument(
        cli_assets.ERROR_ADD_CLI_CMD_DATA,
        '--additional-messages',
    )

    # Assert the argument exists and is typed as dict.
    assert argument is not None
    assert argument['type'] == 'dict'
    assert argument['description'] == (
        'Additional messages beyond the primary one, as lang=text pairs.'
    )

# ** test: list_shaped_json_arguments_remain_json
def test_list_shaped_json_arguments_remain_json():
    '''
    Verify list-shaped arguments out of scope stay type='json'.
    '''

    # Assert app.add --flags remains json when the catalog still exposes it.
    flags_arg = find_argument(cli_assets.APP_ADD_CLI_CMD_DATA, '--flags')
    if flags_arg is not None:
        assert flags_arg['type'] == 'json'

    # Assert cli.add-argument still declares a name_or_flags argument.
    name_or_flags_arg = find_argument(
        cli_assets.CLI_ADD_ARGUMENT_CLI_CMD_DATA,
        'name_or_flags',
    )
    assert name_or_flags_arg is not None

# ** test: feature_get_cli_command_is_registered
def test_feature_get_cli_command_is_registered():
    '''
    Verify feature.get is a registered admin CLI command.
    '''

    # Assert the proto catalog exposes feature.get on the CLI.
    assert hasattr(cli_assets, 'FEATURE_GET_CLI_CMD_ID')
    assert cli_assets.FEATURE_GET_CLI_CMD_ID == 'feature.get'
    assert cli_assets.FEATURE_GET_CLI_CMD_ID in cli_assets.ADMIN_DEFAULT_COMMANDS
