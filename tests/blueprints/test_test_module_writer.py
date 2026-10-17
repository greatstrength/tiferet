"""Tiferet Test Module Writer Tests"""

# *** imports

# ** core
import inspect
from pathlib import Path

# ** infra
import pytest
import yaml

# ** app
import tiferet
import tiferet.blueprints
from tiferet.assets import TiferetError
from tiferet.assets.feature import ADMIN_DEFAULT_FEATURES
from tiferet.blueprints import tester as tester_blueprints
from tiferet.blueprints.tester import (
    add_fixture,
    attach_test,
    detach_test,
    get_fixture,
    list_fixtures,
    remove_fixture,
    update_fixture,
    update_tester,
)
from tiferet.utils.yaml import YamlLoader

# *** constants

# ** constant: preserved_tokens
PRESERVED_TOKENS = (
    '&error_message',
    '*error_message',
    '&plain_message',
    '&lang',
    '*lang',
    '&plain',
    '*plain',
    '&error_module',
    '*error_module',
    '<<:',
    '&formatted',
    '&error_id',
    '*error_id',
    '$fixture.error_message',
    '[error_message, formatted_error_message]',
)

# ** constant: normative_module
NORMATIVE_MODULE = '''fixtures:
  error_message: &error_message
    module_path: &error_module tiferet.domain.error
    class_name: ErrorMessage
    attributes: &plain_message
      lang: &lang en_US
      text: &plain An error occurred.
  formatted_error_message:
    <<: *error_message
    attributes:
      lang: *lang
      text: &formatted 'An error occurred: {error}'
tests:
  error_message_format:
    conditions:
      fixtures: [error_message, formatted_error_message]
    execute:
      - target: error_message
        method: format
        as: raw
    assert:
      - outcome: raw
        equals: *plain
testers:
  test_error:
    module_path: *error_module
    class_name: Error
    id: &error_id TEST_ERROR
    name: Test Error
    message: $fixture.error_message
    fixtures:
      error_message: *error_message
    tests:
      construction_derives_error_code:
        conditions:
          fixtures: []
        execute:
          - target: self
            method: new
            as: built
        assert:
          - outcome: built
            fields:
              id: *error_id
              error_code: *error_id
'''

# ** constant: writer_names
WRITER_NAMES = (
    'add_fixture',
    'get_fixture',
    'list_fixtures',
    'update_fixture',
    'remove_fixture',
    'add_test',
    'get_test',
    'list_tests',
    'update_test',
    'remove_test',
    'add_tester',
    'get_tester',
    'list_testers',
    'update_tester',
    'remove_tester',
    'attach_test',
    'detach_test',
)

# *** functions

# ** function: write_normative
def write_normative(base: Path) -> Path:
    '''
    Write the normative module and return its path.

    :param base: The temporary base directory.
    :type base: Path
    :return: The written counterpart path.
    :rtype: Path
    '''

    # Write the three-root text under tiferet_tests/domain.
    path = base / 'tiferet_tests' / 'domain' / 'test_error.yml'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(NORMATIVE_MODULE, encoding='utf-8')
    return path

# ** function: assert_error
def assert_error(call, code: str) -> None:
    '''
    Assert a call raises TiferetError naming the code. This is not a test.

    :param call: The call to invoke.
    :type call: Callable
    :param code: The error code the message must name.
    :type code: str
    :return: None
    :rtype: None
    '''

    # The cases state the code. This helper only invokes the call.
    with pytest.raises(TiferetError, match=code):
        call()

# *** tests

# ** test: writers_stay_on_the_blueprint
def test_writers_stay_on_the_blueprint() -> None:
    '''
    Read the seventeen writer names, both export lists, and the cache block.

    :return: None
    :rtype: None
    '''

    # Each writer is callable and absent from both package export lists.
    source = Path(tester_blueprints.__file__).read_text()
    for name in WRITER_NAMES:
        assert callable(getattr(tester_blueprints, name))
        assert name not in tiferet.__all__
        assert name not in tiferet.blueprints.__all__

    # The cache block has four catalog decorators and no writer.
    cache_block = source.split(
        '# ** blueprint: build_cache',
        1,
    )[1].split('# ** blueprint: build_tester_context', 1)[0]
    assert cache_block.count('@add_default_') == 4
    assert 'add_fixture' not in cache_block
    assert 'CORE_DEFAULT_FEATURES' not in source
    assert 'tester' not in ADMIN_DEFAULT_FEATURES
    assert 'import pytest' not in source
    assert 'safe_dump' not in source
    assert 'from ..domain' not in source
    assert 'from ..utils' not in source

    # Delegation reads, replaces, and does not name the loader.
    delegation = inspect.getsource(tester_blueprints._delegate_test_module)
    assert 'ReadTestModuleDocument' in delegation
    assert '_read_test_module_text' in delegation
    assert '_replace_test_module' in delegation
    assert 'YamlLoader' not in delegation

    # Each writer delegates and does not replace or handle an event itself.
    for name in WRITER_NAMES:
        writer = inspect.getsource(getattr(tester_blueprints, name))
        assert '_delegate_test_module' in writer
        assert 'os.replace' not in writer
        assert 'DomainEvent.handle' not in writer

    # The loader save path and anchored helper stay on the util this story does not edit.
    assert 'yaml.safe_dump' in inspect.getsource(YamlLoader.save)
    assert 'def anchored' in inspect.getsource(YamlLoader)

# ** test: add_fixture_creates_only_the_test_module
def test_add_fixture_creates_only_the_test_module(tmp_path) -> None:
    '''
    Add one fixture where no counterpart exists.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :return: None
    :rtype: None
    '''

    # Add the fixture at the domain/test_error stem.
    add_fixture(
        'domain/test_error',
        'error_message',
        base_dir=str(tmp_path),
        payload={'class_name': 'ErrorMessage'},
        anchor='error_message',
    )
    path = tmp_path / 'tiferet_tests' / 'domain' / 'test_error.yml'
    text = path.read_text(encoding='utf-8')

    # Only the test module is created, and it starts at fixtures.
    assert path.is_file()
    assert '&error_message' in text
    assert text.startswith('fixtures:')
    assert 'tests:' not in text
    assert 'testers:' not in text
    assert not (tmp_path / 'tests').exists()

# ** test: add_fixture_preserves_recorded_anchors
def test_add_fixture_preserves_recorded_anchors(tmp_path) -> None:
    '''
    Add a later fixture to the normative module.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :return: None
    :rtype: None
    '''

    # Write the normative module, then add extra.
    path = write_normative(tmp_path)
    add_fixture(
        'domain/test_error',
        'extra',
        base_dir=str(tmp_path),
        payload={'class_name': 'Extra'},
    )
    text = path.read_text(encoding='utf-8')

    # Recorded anchors stay, and the merge does not copy module_path into that node.
    for token in PRESERVED_TOKENS:
        assert token in text
    region = text.split('formatted_error_message', 1)[1]
    before_attributes = region.split('attributes:', 1)[0]
    assert 'module_path' not in before_attributes
    dumped = yaml.safe_dump(yaml.safe_load(NORMATIVE_MODULE), sort_keys=True)
    assert text != dumped

# ** test: attach_and_detach_share_the_root_node
def test_attach_and_detach_share_the_root_node(tmp_path) -> None:
    '''
    Attach a root test, attach it again, then detach it.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :return: None
    :rtype: None
    '''

    # Attach the root test by node identity.
    path = write_normative(tmp_path)
    attach_test(
        'domain/test_error',
        'test_error',
        'error_message_format',
        base_dir=str(tmp_path),
    )
    text = path.read_text(encoding='utf-8')
    assert 'error_message_format: &error_message_format' in text
    assert 'error_message_format: *error_message_format' in text
    assert 'construction_derives_error_code' in text

    # The second attach refuses and does not write.
    before = path.read_bytes()
    with pytest.raises(TiferetError, match='TEST_ARTIFACT_ALREADY_EXISTS'):
        attach_test(
            'domain/test_error',
            'test_error',
            'error_message_format',
            base_dir=str(tmp_path),
        )
    assert path.read_bytes() == before

    # Detach leaves the first-visit anchor and drops the alias.
    detach_test(
        'domain/test_error',
        'test_error',
        'error_message_format',
        base_dir=str(tmp_path),
    )
    text = path.read_text(encoding='utf-8')
    assert 'error_message_format: &error_message_format' in text
    assert 'error_message_format: *error_message_format' not in text

# ** test: remove_refuses_to_relocate_a_first_visit
def test_remove_refuses_to_relocate_a_first_visit(tmp_path) -> None:
    '''
    Remove a first-visit fixture, then remove the tester-scoped alias.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :return: None
    :rtype: None
    '''

    # A root remove of a shared first visit does not write.
    path = write_normative(tmp_path)
    before = path.read_bytes()
    with pytest.raises(TiferetError, match='TEST_ANCHOR_CONFLICT'):
        remove_fixture(
            'domain/test_error',
            'error_message',
            base_dir=str(tmp_path),
        )
    assert path.read_bytes() == before

    # The tester-scoped remove drops the alias and leaves the anchor.
    remove_fixture(
        'domain/test_error',
        'error_message',
        base_dir=str(tmp_path),
        tester='test_error',
    )
    text = path.read_text(encoding='utf-8')
    assert '&error_message' in text
    assert 'error_message: *error_message' not in text

# ** test: get_and_list_do_not_write
def test_get_and_list_do_not_write(tmp_path) -> None:
    '''
    Get one aliased fixture and list root and tester fixtures.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :return: None
    :rtype: None
    '''

    # Record the bytes, then read.
    path = write_normative(tmp_path)
    before = path.read_bytes()
    got = get_fixture(
        'domain/test_error',
        'error_message',
        base_dir=str(tmp_path),
        tester='test_error',
    )
    root_names = list_fixtures(
        'domain/test_error',
        base_dir=str(tmp_path),
    )
    tester_names = list_fixtures(
        'domain/test_error',
        base_dir=str(tmp_path),
        tester='test_error',
    )

    # The reads return the alias and do not write.
    assert got['alias'] == 'error_message'
    assert got['fragment'] == '*error_message\n'
    assert 'class_name' not in got['fragment']
    assert root_names == ['error_message', 'formatted_error_message']
    assert 'formatted_error_message' not in tester_names
    assert path.read_bytes() == before

# ** test: update_patches_without_replacing_the_node
def test_update_patches_without_replacing_the_node(tmp_path) -> None:
    '''
    Patch one fixture, then send two refused updates.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :return: None
    :rtype: None
    '''

    # The legal patch leaves the merge key.
    path = write_normative(tmp_path)
    update_fixture(
        'domain/test_error',
        'formatted_error_message',
        base_dir=str(tmp_path),
        payload={'attributes': {'lang': 'en_US'}},
    )
    assert '<<: *error_message' in path.read_text(encoding='utf-8')

    # A tester fixtures payload and a callable payload do not write.
    before = path.read_bytes()
    with pytest.raises(TiferetError, match='TEST_MODULE_WRITE_REFUSED'):
        update_tester(
            'domain/test_error',
            'test_error',
            base_dir=str(tmp_path),
            payload={'fixtures': {}},
        )
    with pytest.raises(TiferetError, match='TEST_MODULE_WRITE_REFUSED'):
        update_fixture(
            'domain/test_error',
            'error_message',
            base_dir=str(tmp_path),
            payload=lambda: None,
        )
    assert path.read_bytes() == before

# ** test: missing_and_illegal_addresses_do_not_create
def test_missing_and_illegal_addresses_do_not_create(tmp_path) -> None:
    '''
    Get a missing stem, two illegal stems, and update an illegal root.

    :param tmp_path: A writable temporary directory.
    :type tmp_path: Path
    :return: None
    :rtype: None
    '''

    # A missing get does not create tiferet_tests.
    with pytest.raises(TiferetError, match='TEST_MODULE_NOT_FOUND'):
        get_fixture(
            'domain/test_missing',
            'error_message',
            base_dir=str(tmp_path),
        )
    assert not (tmp_path / 'tiferet_tests').exists()

    # Illegal stems do not create a module.
    with pytest.raises(TiferetError, match='TEST_MODULE_PATH_INVALID'):
        get_fixture('../config', 'name', base_dir=str(tmp_path))
    with pytest.raises(TiferetError, match='TEST_MODULE_PATH_INVALID'):
        get_fixture('config', 'name', base_dir=str(tmp_path))

    # An illegal root update refuses and leaves the bytes.
    variables = tmp_path / 'tiferet_tests' / 'domain' / 'test_vars.yml'
    variables.parent.mkdir(parents=True)
    variables.write_text('variables:\n  name: kept\n', encoding='utf-8')
    before = variables.read_bytes()
    with pytest.raises(TiferetError, match='TEST_MODULE_WRITE_REFUSED'):
        update_fixture(
            'domain/test_vars',
            'name',
            base_dir=str(tmp_path),
            payload={'a': 1},
        )
    assert variables.read_bytes() == before

# ** test: no_writer_modules_are_added
def test_no_writer_modules_are_added() -> None:
    '''
    Read the named paths and the event module text.

    :return: None
    :rtype: None
    '''

    # The writer stack and the package test tree are absent.
    root = Path(tiferet.__file__).parent
    for relative in (
        'events/tester.py',
        'interfaces/tester.py',
        'mappers/tester.py',
        'repos/tester.py',
    ):
        assert not (root / relative).exists()
    assert not (root / 'tiferet_tests').exists()

    # The yaml event module does not name the retired loader event.
    assert 'LoadYamlMapping' not in (root / 'events/yaml.py').read_text()

    # The tester-module event module keeps the two document verbs and nothing else named here.
    event_text = (root / 'events/tester_module.py').read_text()
    assert (root / 'events/tester_module.py').is_file()
    assert 'class ReadTestModuleDocument' in event_text
    assert 'class WriteTestModuleDocument' in event_text
    for token in (
        'class GetAnchoredYaml',
        'TesterService',
        'yaml.safe_dump',
        'YamlLoader.save',
    ):
        assert token not in event_text
