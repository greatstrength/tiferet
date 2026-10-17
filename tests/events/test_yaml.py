"""Tiferet Yaml Event Tests"""

# *** imports

# ** infra
import pytest
from unittest.mock import Mock

# ** app
from tiferet import use_tester
from tiferet.events.core import DomainEvent, TiferetError
from tiferet.interfaces.core import ServiceError
from tiferet.interfaces.yaml import YamlService
from tiferet.events.yaml import (
    YamlEvent,
    LoadYaml,
    SaveYaml,
    ReadAnchoredYaml,
    WriteAnchoredYaml,
    ListYamlAnchors,
    GetYamlAnchor,
    SetYamlAnchor,
    RemoveYamlAnchor,
    RenameYamlAnchor,
    is_plain_value,
    is_key_path,
)

# *** fixtures

# ** fixture: yaml_service
@pytest.fixture
def yaml_service() -> Mock:
    '''
    A mock YamlService for handle rows.

    :return: A Mock whose spec is YamlService.
    :rtype: Mock
    '''

    # Build a mock whose spec is YamlService.
    return Mock(spec=YamlService)

# *** tests

# ** test: none_is_plain
def test_none_is_plain():
    '''
    Assert a null value is plain.
    '''

    # Call is_plain_value on null.
    outcome = is_plain_value(None)

    # The outcome equals true.
    assert outcome is True

# ** test: string_is_plain
def test_string_is_plain():
    '''
    Assert the string ada is plain.
    '''

    # Call is_plain_value on ada.
    outcome = is_plain_value('ada')

    # The outcome equals true.
    assert outcome is True

# ** test: false_is_plain
def test_false_is_plain():
    '''
    Assert false is plain.
    '''

    # Call is_plain_value on false.
    outcome = is_plain_value(False)

    # The outcome equals true.
    assert outcome is True

# ** test: zero_is_plain
def test_zero_is_plain():
    '''
    Assert 0 is plain.
    '''

    # Call is_plain_value on 0.
    outcome = is_plain_value(0)

    # The outcome equals true.
    assert outcome is True

# ** test: finite_float_is_plain
def test_finite_float_is_plain():
    '''
    Assert 1.5 is plain.
    '''

    # Call is_plain_value on 1.5.
    outcome = is_plain_value(1.5)

    # The outcome equals true.
    assert outcome is True

# ** test: nonfinite_float_rejected
def test_nonfinite_float_rejected():
    '''
    Assert inf, -inf, and nan are not plain.
    '''

    # Call is_plain_value on inf, -inf, and nan.
    outcomes = [
        is_plain_value(value)
        for value in (float('inf'), float('-inf'), float('nan'))
    ]

    # Each outcome equals false.
    assert outcomes == [False, False, False]

# ** test: nested_list_is_plain
def test_nested_list_is_plain():
    '''
    Assert a list of 1, a, null, and false is plain.
    '''

    # Call is_plain_value on that list.
    outcome = is_plain_value([1, 'a', None, False])

    # The outcome equals true.
    assert outcome is True

# ** test: string_keyed_mapping_is_plain
def test_string_keyed_mapping_is_plain():
    '''
    Assert a mapping whose key is a and whose value is a list of 1 is plain.
    '''

    # Call is_plain_value on that mapping.
    outcome = is_plain_value({'a': [1]})

    # The outcome equals true.
    assert outcome is True

# ** test: non_string_key_rejected
def test_non_string_key_rejected():
    '''
    Assert a mapping whose key is 1 is not plain.
    '''

    # Call is_plain_value on a mapping whose key is 1.
    outcome = is_plain_value({1: 'a'})

    # The outcome equals false.
    assert outcome is False

# ** test: tuple_rejected
def test_tuple_rejected():
    '''
    Assert the tuple (1,) is not plain.
    '''

    # Call is_plain_value on the tuple (1,).
    outcome = is_plain_value((1,))

    # The outcome equals false.
    assert outcome is False

# ** test: nested_tuple_rejected
def test_nested_tuple_rejected():
    '''
    Assert a list whose only item is the tuple (1,) is not plain.
    '''

    # Call is_plain_value on a list of that tuple.
    outcome = is_plain_value([(1,)])

    # The outcome equals false.
    assert outcome is False

# ** test: cycle_rejected
def test_cycle_rejected():
    '''
    Assert a list that contains itself is not plain.
    '''

    # Build a list that contains itself.
    value = []
    value.append(value)

    # Call is_plain_value on that list.
    outcome = is_plain_value(value)

    # The outcome equals false.
    assert outcome is False

# ** test: absent_is_path
def test_absent_is_path():
    '''
    Assert a null key path is a path.
    '''

    # Call is_key_path on null.
    outcome = is_key_path(None)

    # The outcome equals true.
    assert outcome is True

# ** test: empty_list_is_root
def test_empty_list_is_root():
    '''
    Assert an empty list is the root path.
    '''

    # Call is_key_path on an empty list.
    outcome = is_key_path([])

    # The outcome equals true.
    assert outcome is True

# ** test: string_path_rejected
def test_string_path_rejected():
    '''
    Assert the string fixtures.user is not a path.
    '''

    # Call is_key_path on fixtures.user.
    outcome = is_key_path('fixtures.user')

    # The outcome equals false.
    assert outcome is False

# ** test: non_list_path_rejected
def test_non_list_path_rejected():
    '''
    Assert the key path 1 is not a path.
    '''

    # Call is_key_path on 1.
    outcome = is_key_path(1)

    # The outcome equals false.
    assert outcome is False

# ** test: step_not_pair
def test_step_not_pair():
    '''
    Assert a step that is the list val is not a path.
    '''

    # Call is_key_path on a list whose only step is ['val'].
    outcome = is_key_path([['val']])

    # The outcome equals false.
    assert outcome is False

# ** test: step_not_list
def test_step_not_list():
    '''
    Assert the list val, user is not a path.
    '''

    # Call is_key_path on ['val', 'user'].
    outcome = is_key_path(['val', 'user'])

    # The outcome equals false.
    assert outcome is False

# ** test: seq_index_accepted
def test_seq_index_accepted():
    '''
    Assert a seq step whose token is 0 is a path.
    '''

    # Call is_key_path on one seq step whose token is 0.
    outcome = is_key_path([['seq', 0]])

    # The outcome equals true.
    assert outcome is True

# ** test: seq_bool_rejected
def test_seq_bool_rejected():
    '''
    Assert a seq step whose token is true is not a path.
    '''

    # Call is_key_path on one seq step whose token is true.
    outcome = is_key_path([['seq', True]])

    # The outcome equals false.
    assert outcome is False

# ** test: seq_negative_rejected
def test_seq_negative_rejected():
    '''
    Assert a seq step whose token is -1 is not a path.
    '''

    # Call is_key_path on one seq step whose token is -1.
    outcome = is_key_path([['seq', -1]])

    # The outcome equals false.
    assert outcome is False

# ** test: val_and_key_accepted
def test_val_and_key_accepted():
    '''
    Assert a val step fixtures then a key step user is a path.
    '''

    # Call is_key_path on those two steps.
    outcome = is_key_path([['val', 'fixtures'], ['key', 'user']])

    # The outcome equals true.
    assert outcome is True

# ** test: bad_kind_rejected
def test_bad_kind_rejected():
    '''
    Assert a step whose kind is id is not a path.
    '''

    # Call is_key_path on one step, kind id, token user.
    outcome = is_key_path([['id', 'user']])

    # The outcome equals false.
    assert outcome is False

# ** test: non_string_token_rejected
def test_non_string_token_rejected():
    '''
    Assert a val step whose token is 1 is not a path.
    '''

    # Call is_key_path on one val step whose token is 1.
    outcome = is_key_path([['val', 1]])

    # The outcome equals false.
    assert outcome is False

# *** testers

# ** tester: test_yaml_event
class TestYamlEvent:
    '''
    Tests for YamlEvent.
    '''

    # * test: event_base
    def test_event_base(self, yaml_service):
        '''
        Assert YamlEvent is a DomainEvent and stores the injected service.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Construct the subject with the fixture mock.
        outcome = YamlEvent(yaml_service=yaml_service)

        # The subject is a subclass of DomainEvent.
        assert issubclass(YamlEvent, DomainEvent)

        # The outcome's yaml_service is that same mock.
        assert outcome.yaml_service is yaml_service

# ** tester: test_load_yaml
@use_tester(
    type='domain_event',
    target_cls=LoadYaml,
    dependencies={
        'yaml_service': {
            'module_path': 'tiferet.interfaces.yaml',
            'class_name': 'YamlService',
        },
    },
    sample_kwargs={
        'path': 'notes.yml',
    },
    required_params=[
        'path',
    ],
)
class TestLoadYaml:
    '''
    Tests for LoadYaml.
    '''

    # * test: load_mapping
    def test_load_mapping(self, yaml_service):
        '''
        Assert load returns the mapping and calls load_mapping with the path.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange load_mapping to return a mapping whose name is first.
        expected = {'name': 'first'}
        yaml_service.load_mapping.return_value = expected

        # Handle with path notes.yml.
        outcome = DomainEvent.handle(
            LoadYaml,
            dependencies={'yaml_service': yaml_service},
            path='notes.yml',
        )

        # The outcome equals that mapping. The call arguments equal notes.yml.
        assert outcome == expected
        assert list(yaml_service.load_mapping.call_args.args) == ['notes.yml']

    # * test: missing_path
    def test_missing_path(self, yaml_service):
        '''
        Assert a null path raises COMMAND_PARAMETER_REQUIRED naming LoadYaml.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Handle with a null path.
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                LoadYaml,
                dependencies={'yaml_service': yaml_service},
                path=None,
            )

        # The message names COMMAND_PARAMETER_REQUIRED and LoadYaml.
        message = str(exc_info.value)
        assert 'COMMAND_PARAMETER_REQUIRED' in message
        assert 'LoadYaml' in message

    # * test: blank_path
    def test_blank_path(self, yaml_service):
        '''
        Assert a whitespace path raises COMMAND_PARAMETER_REQUIRED naming LoadYaml.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Handle with a whitespace path.
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                LoadYaml,
                dependencies={'yaml_service': yaml_service},
                path='   ',
            )

        # The message names COMMAND_PARAMETER_REQUIRED and LoadYaml.
        message = str(exc_info.value)
        assert 'COMMAND_PARAMETER_REQUIRED' in message
        assert 'LoadYaml' in message

    # * test: service_error_propagates
    def test_service_error_propagates(self, yaml_service):
        '''
        Assert a missing-file service error propagates and is not a domain error.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange load_mapping to raise YAML_FILE_NOT_FOUND.
        yaml_service.load_mapping.side_effect = ServiceError(
            'YAML_FILE_NOT_FOUND',
            message='YAML_FILE_NOT_FOUND',
        )

        # Handle with path missing.yml.
        with pytest.raises(ServiceError) as exc_info:
            DomainEvent.handle(
                LoadYaml,
                dependencies={'yaml_service': yaml_service},
                path='missing.yml',
            )

        # The message names YAML_FILE_NOT_FOUND. The outcome is not a TiferetError.
        assert 'YAML_FILE_NOT_FOUND' in str(exc_info.value)
        assert not isinstance(exc_info.value, TiferetError)

    # * test: mapping_required_propagates
    def test_mapping_required_propagates(self, yaml_service):
        '''
        Assert a mapping-required service error propagates.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange load_mapping to raise YAML_MAPPING_REQUIRED.
        yaml_service.load_mapping.side_effect = ServiceError(
            'YAML_MAPPING_REQUIRED',
            message='YAML_MAPPING_REQUIRED',
        )

        # Handle with path list.yml.
        with pytest.raises(ServiceError) as exc_info:
            DomainEvent.handle(
                LoadYaml,
                dependencies={'yaml_service': yaml_service},
                path='list.yml',
            )

        # The message names YAML_MAPPING_REQUIRED.
        assert 'YAML_MAPPING_REQUIRED' in str(exc_info.value)

# ** tester: test_save_yaml
@use_tester(
    type='domain_event',
    target_cls=SaveYaml,
    dependencies={
        'yaml_service': {
            'module_path': 'tiferet.interfaces.yaml',
            'class_name': 'YamlService',
        },
    },
    sample_kwargs={
        'path': 'saved.yml',
        'data': {
            'name': 'saved',
            'count': 2,
        },
    },
    required_params=[
        'path',
        'data',
    ],
)
class TestSaveYaml:
    '''
    Tests for SaveYaml.
    '''

    # * test: save_mapping
    def test_save_mapping(self, yaml_service):
        '''
        Assert save returns the mapping and passes that mapping to the service.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange save_mapping to return the written mapping.
        expected = {'name': 'saved', 'count': 2}
        yaml_service.save_mapping.return_value = expected

        # Handle with path saved.yml and that mapping as data.
        outcome = DomainEvent.handle(
            SaveYaml,
            dependencies={'yaml_service': yaml_service},
            path='saved.yml',
            data=expected,
        )

        # The outcome equals that mapping. The call arguments equal the path and mapping.
        assert outcome == expected
        assert yaml_service.save_mapping.call_args.args == ('saved.yml', expected)

    # * test: empty_mapping
    def test_empty_mapping(self, yaml_service):
        '''
        Assert an empty mapping is a success.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange save_mapping to return an empty mapping.
        yaml_service.save_mapping.return_value = {}

        # Handle with path empty-map.yml and data {}.
        outcome = DomainEvent.handle(
            SaveYaml,
            dependencies={'yaml_service': yaml_service},
            path='empty-map.yml',
            data={},
        )

        # The outcome equals {}. The call arguments equal the path and {}.
        assert outcome == {}
        assert yaml_service.save_mapping.call_args.args == ('empty-map.yml', {})

    # * test: missing_data
    def test_missing_data(self, yaml_service):
        '''
        Assert a null data value raises COMMAND_PARAMETER_REQUIRED naming SaveYaml.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Handle with path saved.yml and null data.
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                SaveYaml,
                dependencies={'yaml_service': yaml_service},
                path='saved.yml',
                data=None,
            )

        # The message names COMMAND_PARAMETER_REQUIRED and SaveYaml.
        message = str(exc_info.value)
        assert 'COMMAND_PARAMETER_REQUIRED' in message
        assert 'SaveYaml' in message

# ** tester: test_read_anchored_yaml
@use_tester(
    type='domain_event',
    target_cls=ReadAnchoredYaml,
    dependencies={
        'yaml_service': {
            'module_path': 'tiferet.interfaces.yaml',
            'class_name': 'YamlService',
        },
    },
    sample_kwargs={
        'path': 'anchored.yml',
    },
    required_params=[
        'path',
    ],
)
class TestReadAnchoredYaml:
    '''
    Tests for ReadAnchoredYaml.
    '''

    # * test: read_anchored
    def test_read_anchored(self, yaml_service):
        '''
        Assert read returns the text and names and calls read_anchored with the path.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange read_anchored. The text is not a line break.
        text = 'item: &item\\n'
        expected = {'text': text, 'anchors': ['item']}
        yaml_service.read_anchored.return_value = expected

        # Handle with path anchored.yml.
        outcome = DomainEvent.handle(
            ReadAnchoredYaml,
            dependencies={'yaml_service': yaml_service},
            path='anchored.yml',
        )

        # The outcome equals that mapping. The call arguments equal anchored.yml.
        assert outcome == expected
        assert list(yaml_service.read_anchored.call_args.args) == ['anchored.yml']

# ** tester: test_write_anchored_yaml
@use_tester(
    type='domain_event',
    target_cls=WriteAnchoredYaml,
    dependencies={
        'yaml_service': {
            'module_path': 'tiferet.interfaces.yaml',
            'class_name': 'YamlService',
        },
    },
    sample_kwargs={
        'path': 'anchored.yml',
        'text': 'item: &item\\n',
    },
    required_params=[
        'path',
        'text',
    ],
)
class TestWriteAnchoredYaml:
    '''
    Tests for WriteAnchoredYaml.
    '''

    # * test: write_anchored
    def test_write_anchored(self, yaml_service):
        '''
        Assert write returns the text and names and passes that text through.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange write_anchored. The text is not a line break.
        text = 'item: &item\\n'
        expected = {'text': text, 'anchors': ['item']}
        yaml_service.write_anchored.return_value = expected

        # Handle with path anchored.yml and that text.
        outcome = DomainEvent.handle(
            WriteAnchoredYaml,
            dependencies={'yaml_service': yaml_service},
            path='anchored.yml',
            text=text,
        )

        # The outcome equals that mapping. The call arguments equal the path and text.
        assert outcome == expected
        assert yaml_service.write_anchored.call_args.args == ('anchored.yml', text)

    # * test: blank_text
    def test_blank_text(self, yaml_service):
        '''
        Assert whitespace text raises COMMAND_PARAMETER_REQUIRED naming WriteAnchoredYaml.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Handle with path anchored.yml and whitespace text.
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                WriteAnchoredYaml,
                dependencies={'yaml_service': yaml_service},
                path='anchored.yml',
                text='   ',
            )

        # The message names COMMAND_PARAMETER_REQUIRED and WriteAnchoredYaml.
        message = str(exc_info.value)
        assert 'COMMAND_PARAMETER_REQUIRED' in message
        assert 'WriteAnchoredYaml' in message

    # * test: anchor_conflict_propagates
    def test_anchor_conflict_propagates(self, yaml_service):
        '''
        Assert an anchor-conflict service error propagates.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange write_anchored to raise YAML_ANCHOR_CONFLICT.
        text = 'a: &item 1\\n'
        yaml_service.write_anchored.side_effect = ServiceError(
            'YAML_ANCHOR_CONFLICT',
            message='YAML_ANCHOR_CONFLICT',
        )

        # Handle with path conflict.yml and that text. The text is not a line break.
        with pytest.raises(ServiceError) as exc_info:
            DomainEvent.handle(
                WriteAnchoredYaml,
                dependencies={'yaml_service': yaml_service},
                path='conflict.yml',
                text=text,
            )

        # The message names YAML_ANCHOR_CONFLICT.
        assert 'YAML_ANCHOR_CONFLICT' in str(exc_info.value)

# ** tester: test_list_yaml_anchors
@use_tester(
    type='domain_event',
    target_cls=ListYamlAnchors,
    dependencies={
        'yaml_service': {
            'module_path': 'tiferet.interfaces.yaml',
            'class_name': 'YamlService',
        },
    },
    sample_kwargs={
        'path': 'notes.yml',
    },
    required_params=[
        'path',
    ],
)
class TestListYamlAnchors:
    '''
    Tests for ListYamlAnchors.
    '''

    # * test: list_anchors
    def test_list_anchors(self, yaml_service):
        '''
        Assert list returns the names and does not forward key_path.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange list_anchors to return first, second.
        expected = ['first', 'second']
        yaml_service.list_anchors.return_value = expected

        # Handle with path notes.yml and an ignored key_path.
        outcome = DomainEvent.handle(
            ListYamlAnchors,
            dependencies={'yaml_service': yaml_service},
            path='notes.yml',
            key_path='ignored',
        )

        # The outcome equals that list. key_path is not a call argument.
        assert outcome == expected
        assert list(yaml_service.list_anchors.call_args.args) == ['notes.yml']
        assert 'key_path' not in yaml_service.list_anchors.call_args.kwargs
        assert 'key_path' not in yaml_service.list_anchors.call_args.args

    # * test: empty_list
    def test_empty_list(self, yaml_service):
        '''
        Assert an empty anchor list is a success.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange list_anchors to return an empty list.
        yaml_service.list_anchors.return_value = []

        # Handle with path empty.yml.
        outcome = DomainEvent.handle(
            ListYamlAnchors,
            dependencies={'yaml_service': yaml_service},
            path='empty.yml',
        )

        # The outcome equals [].
        assert outcome == []

    # * test: missing_path
    def test_missing_path(self, yaml_service):
        '''
        Assert a null path raises COMMAND_PARAMETER_REQUIRED naming ListYamlAnchors.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Handle with a null path.
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                ListYamlAnchors,
                dependencies={'yaml_service': yaml_service},
                path=None,
            )

        # The message names COMMAND_PARAMETER_REQUIRED and ListYamlAnchors.
        message = str(exc_info.value)
        assert 'COMMAND_PARAMETER_REQUIRED' in message
        assert 'ListYamlAnchors' in message

    # * test: blank_path
    def test_blank_path(self, yaml_service):
        '''
        Assert a whitespace path raises COMMAND_PARAMETER_REQUIRED naming ListYamlAnchors.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Handle with a whitespace path.
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                ListYamlAnchors,
                dependencies={'yaml_service': yaml_service},
                path='   ',
            )

        # The message names COMMAND_PARAMETER_REQUIRED and ListYamlAnchors.
        message = str(exc_info.value)
        assert 'COMMAND_PARAMETER_REQUIRED' in message
        assert 'ListYamlAnchors' in message

# ** tester: test_get_yaml_anchor
@use_tester(
    type='domain_event',
    target_cls=GetYamlAnchor,
    dependencies={
        'yaml_service': {
            'module_path': 'tiferet.interfaces.yaml',
            'class_name': 'YamlService',
        },
    },
    sample_kwargs={
        'path': 'notes.yml',
        'name': 'item',
    },
    required_params=[
        'path',
        'name',
    ],
)
class TestGetYamlAnchor:
    '''
    Tests for GetYamlAnchor.
    '''

    # * test: null_value
    def test_null_value(self, yaml_service):
        '''
        Assert a null anchor value is returned and key_path is not forwarded.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange get_anchor to return a null value.
        expected = {'value': None}
        yaml_service.get_anchor.return_value = expected

        # Handle with path notes.yml, name item, and an ignored key_path.
        outcome = DomainEvent.handle(
            GetYamlAnchor,
            dependencies={'yaml_service': yaml_service},
            path='notes.yml',
            name='item',
            key_path='ignored',
        )

        # The value field is null. key_path is not a call argument.
        assert outcome == expected
        assert outcome['value'] is None
        assert yaml_service.get_anchor.call_args.args == ('notes.yml', 'item')
        assert 'key_path' not in yaml_service.get_anchor.call_args.kwargs

    # * test: star_string
    def test_star_string(self, yaml_service):
        '''
        Assert a star string is returned as text, not expanded.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange get_anchor to return the string *other.
        expected = {'value': '*other'}
        yaml_service.get_anchor.return_value = expected

        # Handle with path notes.yml and name item.
        outcome = DomainEvent.handle(
            GetYamlAnchor,
            dependencies={'yaml_service': yaml_service},
            path='notes.yml',
            name='item',
        )

        # The value field equals *other.
        assert outcome == expected
        assert outcome['value'] == '*other'

    # * test: blank_name
    def test_blank_name(self, yaml_service):
        '''
        Assert a whitespace name raises COMMAND_PARAMETER_REQUIRED naming GetYamlAnchor.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Handle with path notes.yml and a whitespace name.
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                GetYamlAnchor,
                dependencies={'yaml_service': yaml_service},
                path='notes.yml',
                name='   ',
            )

        # The message names COMMAND_PARAMETER_REQUIRED and GetYamlAnchor.
        message = str(exc_info.value)
        assert 'COMMAND_PARAMETER_REQUIRED' in message
        assert 'GetYamlAnchor' in message

    # * test: service_error_propagates
    def test_service_error_propagates(self, yaml_service):
        '''
        Assert a missing-anchor service error propagates and is not a domain error.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange get_anchor to raise YAML_ANCHOR_NOT_FOUND.
        yaml_service.get_anchor.side_effect = ServiceError(
            'YAML_ANCHOR_NOT_FOUND',
            message='YAML_ANCHOR_NOT_FOUND',
        )

        # Handle with path notes.yml and name missing.
        with pytest.raises(ServiceError) as exc_info:
            DomainEvent.handle(
                GetYamlAnchor,
                dependencies={'yaml_service': yaml_service},
                path='notes.yml',
                name='missing',
            )

        # The message names YAML_ANCHOR_NOT_FOUND. The outcome is not a TiferetError.
        assert 'YAML_ANCHOR_NOT_FOUND' in str(exc_info.value)
        assert not isinstance(exc_info.value, TiferetError)

# ** tester: test_set_yaml_anchor
@use_tester(
    type='domain_event',
    target_cls=SetYamlAnchor,
    dependencies={
        'yaml_service': {
            'module_path': 'tiferet.interfaces.yaml',
            'class_name': 'YamlService',
        },
    },
    sample_kwargs={
        'path': 'notes.yml',
        'name': 'user',
        'value': 'ada',
    },
    required_params=[
        'path',
        'name',
    ],
)
class TestSetYamlAnchor:
    '''
    Tests for SetYamlAnchor.
    '''

    # * test: set_value
    def test_set_value(self, yaml_service):
        '''
        Assert set passes the value and the key path as keywords.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange set_anchor to return ada.
        expected = {'value': 'ada'}
        key_path = [['val', 'fixtures'], ['val', 'user']]
        yaml_service.set_anchor.return_value = expected

        # Handle with the path, name, value, and that key path.
        outcome = DomainEvent.handle(
            SetYamlAnchor,
            dependencies={'yaml_service': yaml_service},
            path='notes.yml',
            name='user',
            value='ada',
            key_path=key_path,
        )

        # The call arguments are the path and name. The keywords are the value and path.
        assert outcome == expected
        assert yaml_service.set_anchor.call_args.args == ('notes.yml', 'user')
        assert yaml_service.set_anchor.call_args.kwargs == {
            'value': 'ada',
            'key_path': key_path,
        }

    # * test: empty_string
    def test_empty_string(self, yaml_service):
        '''
        Assert an empty string is a legal value and an omitted path is null.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange set_anchor to return an empty string.
        expected = {'value': ''}
        yaml_service.set_anchor.return_value = expected

        # Handle with an empty string and no key path.
        outcome = DomainEvent.handle(
            SetYamlAnchor,
            dependencies={'yaml_service': yaml_service},
            path='notes.yml',
            name='item',
            value='',
        )

        # The keywords equal value '' and key_path null.
        assert outcome == expected
        assert yaml_service.set_anchor.call_args.kwargs == {
            'value': '',
            'key_path': None,
        }

    # * test: null_value
    def test_null_value(self, yaml_service):
        '''
        Assert null is a legal value and is passed through.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange set_anchor to return a null value.
        expected = {'value': None}
        yaml_service.set_anchor.return_value = expected

        # Handle with a null value.
        outcome = DomainEvent.handle(
            SetYamlAnchor,
            dependencies={'yaml_service': yaml_service},
            path='notes.yml',
            name='item',
            value=None,
        )

        # The value field is null. The keywords equal value null and key_path null.
        assert outcome == expected
        assert outcome['value'] is None
        assert yaml_service.set_anchor.call_args.kwargs == {
            'value': None,
            'key_path': None,
        }

    # * test: empty_key_path
    def test_empty_key_path(self, yaml_service):
        '''
        Assert an empty key path is passed through as the root.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange set_anchor to return 1.
        expected = {'value': 1}
        yaml_service.set_anchor.return_value = expected

        # Handle with value 1 and an empty key path.
        outcome = DomainEvent.handle(
            SetYamlAnchor,
            dependencies={'yaml_service': yaml_service},
            path='notes.yml',
            name='item',
            value=1,
            key_path=[],
        )

        # The keywords equal value 1 and key_path [].
        assert outcome == expected
        assert yaml_service.set_anchor.call_args.kwargs == {
            'value': 1,
            'key_path': [],
        }

    # * test: omitted_value
    def test_omitted_value(self, yaml_service):
        '''
        Assert an omitted value raises before the service is called.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Handle without sending value.
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                SetYamlAnchor,
                dependencies={'yaml_service': yaml_service},
                path='notes.yml',
                name='item',
            )

        # The message names the required-value sentence. set_anchor is not called.
        assert 'A value is required to set an anchor.' in str(exc_info.value)
        assert yaml_service.set_anchor.call_count == 0

    # * test: blank_path
    def test_blank_path(self, yaml_service):
        '''
        Assert a whitespace path raises COMMAND_PARAMETER_REQUIRED naming SetYamlAnchor.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Handle with a whitespace path, name item, and an empty value.
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                SetYamlAnchor,
                dependencies={'yaml_service': yaml_service},
                path='   ',
                name='item',
                value='',
            )

        # The message names COMMAND_PARAMETER_REQUIRED and SetYamlAnchor.
        message = str(exc_info.value)
        assert 'COMMAND_PARAMETER_REQUIRED' in message
        assert 'SetYamlAnchor' in message

    # * test: rejects_tuple
    def test_rejects_tuple(self, yaml_service):
        '''
        Assert a tuple value is rejected before the service is called.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Handle with the tuple (1,).
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                SetYamlAnchor,
                dependencies={'yaml_service': yaml_service},
                path='notes.yml',
                name='item',
                value=(1,),
            )

        # The message names the plain-value sentence. set_anchor is not called.
        assert 'An anchor value must be a plain value.' in str(exc_info.value)
        assert yaml_service.set_anchor.call_count == 0

    # * test: value_required_propagates
    def test_value_required_propagates(self, yaml_service):
        '''
        Assert an omitted value is a domain error, not the armed service error.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arm set_anchor to raise YAML_ANCHOR_VALUE_REQUIRED. Do not send value.
        armed = ServiceError(
            'YAML_ANCHOR_VALUE_REQUIRED',
            message='YAML_ANCHOR_VALUE_REQUIRED',
        )
        yaml_service.set_anchor.side_effect = armed

        # Handle with path notes.yml and name item.
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                SetYamlAnchor,
                dependencies={'yaml_service': yaml_service},
                path='notes.yml',
                name='item',
            )

        # The domain sentence is the outcome. The armed service error is not.
        assert 'A value is required to set an anchor.' in str(exc_info.value)
        assert not isinstance(exc_info.value, ServiceError)
        assert exc_info.value is not armed

    # * test: plain_value_propagates
    def test_plain_value_propagates(self, yaml_service):
        '''
        Assert a plain-value service error propagates when the value is plain.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange set_anchor to raise YAML_PLAIN_VALUE_REQUIRED.
        yaml_service.set_anchor.side_effect = ServiceError(
            'YAML_PLAIN_VALUE_REQUIRED',
            message='YAML_PLAIN_VALUE_REQUIRED',
        )

        # Handle with the plain string ada.
        with pytest.raises(ServiceError) as exc_info:
            DomainEvent.handle(
                SetYamlAnchor,
                dependencies={'yaml_service': yaml_service},
                path='notes.yml',
                name='item',
                value='ada',
            )

        # The message names YAML_PLAIN_VALUE_REQUIRED.
        assert 'YAML_PLAIN_VALUE_REQUIRED' in str(exc_info.value)

    # * test: key_path_propagates
    def test_key_path_propagates(self, yaml_service):
        '''
        Assert a malformed key path is a domain error, not the armed service error.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arm set_anchor to raise YAML_KEY_PATH_INVALID.
        armed = ServiceError(
            'YAML_KEY_PATH_INVALID',
            message='YAML_KEY_PATH_INVALID',
        )
        yaml_service.set_anchor.side_effect = armed

        # Handle with a dot-string key path.
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                SetYamlAnchor,
                dependencies={'yaml_service': yaml_service},
                path='missing.yml',
                name='item',
                value=1,
                key_path='fixtures.user',
            )

        # The domain sentence is the outcome. The armed service error is not.
        message = str(exc_info.value)
        assert 'A key path must be a list of val, key, or seq steps.' in message
        assert not isinstance(exc_info.value, ServiceError)
        assert exc_info.value is not armed

    # * test: file_not_found_propagates
    def test_file_not_found_propagates(self, yaml_service):
        '''
        Assert a missing-file service error propagates.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange set_anchor to raise YAML_FILE_NOT_FOUND.
        yaml_service.set_anchor.side_effect = ServiceError(
            'YAML_FILE_NOT_FOUND',
            message='YAML_FILE_NOT_FOUND',
        )

        # Handle with path missing.yml, name item, and value 1.
        with pytest.raises(ServiceError) as exc_info:
            DomainEvent.handle(
                SetYamlAnchor,
                dependencies={'yaml_service': yaml_service},
                path='missing.yml',
                name='item',
                value=1,
            )

        # The message names YAML_FILE_NOT_FOUND.
        assert 'YAML_FILE_NOT_FOUND' in str(exc_info.value)

    # * test: anchor_conflict_propagates
    def test_anchor_conflict_propagates(self, yaml_service):
        '''
        Assert an anchor-conflict service error propagates and is not a domain error.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange set_anchor to raise YAML_ANCHOR_CONFLICT.
        yaml_service.set_anchor.side_effect = ServiceError(
            'YAML_ANCHOR_CONFLICT',
            message='YAML_ANCHOR_CONFLICT',
        )

        # Handle with path notes.yml, name item, and value 1.
        with pytest.raises(ServiceError) as exc_info:
            DomainEvent.handle(
                SetYamlAnchor,
                dependencies={'yaml_service': yaml_service},
                path='notes.yml',
                name='item',
                value=1,
            )

        # The message names YAML_ANCHOR_CONFLICT. The outcome is not a TiferetError.
        assert 'YAML_ANCHOR_CONFLICT' in str(exc_info.value)
        assert not isinstance(exc_info.value, TiferetError)

# ** tester: test_remove_yaml_anchor
@use_tester(
    type='domain_event',
    target_cls=RemoveYamlAnchor,
    dependencies={
        'yaml_service': {
            'module_path': 'tiferet.interfaces.yaml',
            'class_name': 'YamlService',
        },
    },
    sample_kwargs={
        'path': 'notes.yml',
        'name': 'item',
    },
    required_params=[
        'path',
        'name',
    ],
)
class TestRemoveYamlAnchor:
    '''
    Tests for RemoveYamlAnchor.
    '''

    # * test: remove_anchor
    def test_remove_anchor(self, yaml_service):
        '''
        Assert remove returns the name and does not forward key_path.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange remove_anchor to return item.
        yaml_service.remove_anchor.return_value = 'item'

        # Handle with path notes.yml, name item, and an ignored key_path.
        outcome = DomainEvent.handle(
            RemoveYamlAnchor,
            dependencies={'yaml_service': yaml_service},
            path='notes.yml',
            name='item',
            key_path='ignored',
        )

        # The outcome equals item. key_path is not a call argument.
        assert outcome == 'item'
        assert yaml_service.remove_anchor.call_args.args == ('notes.yml', 'item')
        assert 'key_path' not in yaml_service.remove_anchor.call_args.kwargs

    # * test: blank_name
    def test_blank_name(self, yaml_service):
        '''
        Assert an empty name raises COMMAND_PARAMETER_REQUIRED naming RemoveYamlAnchor.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Handle with path notes.yml and an empty name.
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                RemoveYamlAnchor,
                dependencies={'yaml_service': yaml_service},
                path='notes.yml',
                name='',
            )

        # The message names COMMAND_PARAMETER_REQUIRED and RemoveYamlAnchor.
        message = str(exc_info.value)
        assert 'COMMAND_PARAMETER_REQUIRED' in message
        assert 'RemoveYamlAnchor' in message

    # * test: anchor_conflict_propagates
    def test_anchor_conflict_propagates(self, yaml_service):
        '''
        Assert an anchor-conflict service error propagates.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange remove_anchor to raise YAML_ANCHOR_CONFLICT.
        yaml_service.remove_anchor.side_effect = ServiceError(
            'YAML_ANCHOR_CONFLICT',
            message='YAML_ANCHOR_CONFLICT',
        )

        # Handle with path notes.yml and name item.
        with pytest.raises(ServiceError) as exc_info:
            DomainEvent.handle(
                RemoveYamlAnchor,
                dependencies={'yaml_service': yaml_service},
                path='notes.yml',
                name='item',
            )

        # The message names YAML_ANCHOR_CONFLICT.
        assert 'YAML_ANCHOR_CONFLICT' in str(exc_info.value)

# ** tester: test_rename_yaml_anchor
@use_tester(
    type='domain_event',
    target_cls=RenameYamlAnchor,
    dependencies={
        'yaml_service': {
            'module_path': 'tiferet.interfaces.yaml',
            'class_name': 'YamlService',
        },
    },
    sample_kwargs={
        'path': 'notes.yml',
        'name': 'item',
        'new_name': 'next',
    },
    required_params=[
        'path',
        'name',
        'new_name',
    ],
)
class TestRenameYamlAnchor:
    '''
    Tests for RenameYamlAnchor.
    '''

    # * test: rename_anchor
    def test_rename_anchor(self, yaml_service):
        '''
        Assert rename returns the recorded name and does not forward key_path.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange rename_anchor to return next.
        yaml_service.rename_anchor.return_value = 'next'

        # Handle with the current name, the new name, and an ignored key_path.
        outcome = DomainEvent.handle(
            RenameYamlAnchor,
            dependencies={'yaml_service': yaml_service},
            path='notes.yml',
            name='item',
            new_name='next',
            key_path='ignored',
        )

        # The outcome equals next. key_path is not a call argument.
        assert outcome == 'next'
        assert yaml_service.rename_anchor.call_args.args == ('notes.yml', 'item', 'next')
        assert 'key_path' not in yaml_service.rename_anchor.call_args.kwargs

    # * test: same_name
    def test_same_name(self, yaml_service):
        '''
        Assert renaming an anchor to its current name returns that name.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange rename_anchor to return item.
        yaml_service.rename_anchor.return_value = 'item'

        # Handle with the same name on both sides.
        outcome = DomainEvent.handle(
            RenameYamlAnchor,
            dependencies={'yaml_service': yaml_service},
            path='notes.yml',
            name='item',
            new_name='item',
        )

        # The outcome equals item.
        assert outcome == 'item'

    # * test: blank_new_name
    def test_blank_new_name(self, yaml_service):
        '''
        Assert whitespace new_name raises COMMAND_PARAMETER_REQUIRED naming RenameYamlAnchor.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Handle with a whitespace new name.
        with pytest.raises(TiferetError) as exc_info:
            DomainEvent.handle(
                RenameYamlAnchor,
                dependencies={'yaml_service': yaml_service},
                path='notes.yml',
                name='item',
                new_name='   ',
            )

        # The message names COMMAND_PARAMETER_REQUIRED and RenameYamlAnchor.
        message = str(exc_info.value)
        assert 'COMMAND_PARAMETER_REQUIRED' in message
        assert 'RenameYamlAnchor' in message

    # * test: anchor_conflict_propagates
    def test_anchor_conflict_propagates(self, yaml_service):
        '''
        Assert an anchor-conflict service error propagates and is not a domain error.

        :param yaml_service: The mock YamlService fixture.
        :type yaml_service: Mock
        '''

        # Arrange rename_anchor to raise YAML_ANCHOR_CONFLICT.
        yaml_service.rename_anchor.side_effect = ServiceError(
            'YAML_ANCHOR_CONFLICT',
            message='YAML_ANCHOR_CONFLICT',
        )

        # Handle with new_name other.
        with pytest.raises(ServiceError) as exc_info:
            DomainEvent.handle(
                RenameYamlAnchor,
                dependencies={'yaml_service': yaml_service},
                path='notes.yml',
                name='item',
                new_name='other',
            )

        # The message names YAML_ANCHOR_CONFLICT. The outcome is not a TiferetError.
        assert 'YAML_ANCHOR_CONFLICT' in str(exc_info.value)
        assert not isinstance(exc_info.value, TiferetError)
