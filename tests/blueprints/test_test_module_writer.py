"""Tiferet Test Module Writer Tests"""

# *** imports

# ** core
import inspect
from pathlib import Path

# ** infra
import yaml

# ** app
import tiferet
import tiferet.blueprints
from tiferet import TiferetError
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
    attributes:
      id: &error_id TEST_ERROR
      name: Test Error
      message: [$fixture.error_message]
    fixtures:
      error_message: *error_message
    tests:
      construction_derives_error_code:
        conditions:
          fixtures: [error_message]
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

# *** functions

# ** function: write_normative
def _write_normative(base_dir) -> object:
    '''Write the RFP-027 snippet under a temporary base directory.'''

    path = base_dir / 'tiferet_tests' / 'domain' / 'test_error.yml'
    path.parent.mkdir(parents=True)
    path.write_text(NORMATIVE_MODULE)
    return path

# ** function: assert_error
def _assert_error(operation, error_id: str) -> None:
    '''Assert a writer raises the named TiferetError id.'''

    try:
        operation()
    except TiferetError as error:
        assert error.error_code == error_id
        return
    raise AssertionError(error_id)

# *** tests

# ** test: writers_stay_on_the_blueprint
def test_writers_stay_on_the_blueprint() -> None:
    '''The seventeen writers are blueprint functions and are not package exports.'''

    names = (
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

    # The functions exist on the blueprint and nowhere in the package roots.
    for name in names:
        assert callable(getattr(tester_blueprints, name))
        assert name not in tiferet.__all__
        assert name not in tiferet.blueprints.__all__

    # The cache decorators and the application feature catalog stay untouched.
    module_source = inspect.getsource(tester_blueprints)
    cache_block = module_source.split('# ** blueprint: build_cache', 1)[1]
    cache_block = cache_block.split('# ** blueprint: build_tester_context', 1)[0]
    assert cache_block.count('@add_default_') == 4
    assert 'add_fixture' not in cache_block
    assert 'CORE_DEFAULT_FEATURES' not in module_source
    assert 'tester' not in ADMIN_DEFAULT_FEATURES

    # The writer does not import pytest or dump through safe_dump.
    assert 'import pytest' not in module_source
    assert 'safe_dump' not in module_source
    assert 'YamlLoader' not in module_source
    assert 'from ..domain' not in module_source
    assert 'from ..utils' not in module_source
    assert 'yaml.safe_dump' in inspect.getsource(YamlLoader.save)
    assert 'def anchored' in inspect.getsource(YamlLoader)

# ** test: add_fixture_creates_only_the_test_module
def test_add_fixture_creates_only_the_test_module(tmp_path) -> None:
    '''A root add creates tiferet_tests/<rel>.yml and no tests/ file.'''

    add_fixture(
        'domain/test_error',
        'error_message',
        payload={'class_name': 'ErrorMessage'},
        anchor='error_message',
        base_dir=tmp_path,
    )
    path = tmp_path / 'tiferet_tests' / 'domain' / 'test_error.yml'
    text = path.read_text()

    # The new file has the anchor and only the fixtures root.
    assert path.is_file()
    assert '&error_message' in text
    assert text.startswith('fixtures:')
    assert 'tests:' not in text
    assert 'testers:' not in text
    assert not (tmp_path / 'tests').exists()

# ** test: add_fixture_preserves_recorded_anchors
def test_add_fixture_preserves_recorded_anchors(tmp_path) -> None:
    '''A later add keeps the normative anchors and is not a safe_dump round-trip.'''

    path = _write_normative(tmp_path)
    add_fixture(
        'domain/test_error',
        'extra',
        payload={'class_name': 'Extra'},
        base_dir=tmp_path,
    )
    text = path.read_text()

    # Every recorded token survives, and the merged fixture is not expanded.
    for token in PRESERVED_TOKENS:
        assert token in text
    merged = text.split('formatted_error_message:', 1)[1].split('tests:', 1)[0]
    assert 'module_path' not in merged.split('attributes:', 1)[0]
    assert text != yaml.safe_dump(yaml.safe_load(NORMATIVE_MODULE), sort_keys=False)

# ** test: attach_and_detach_share_the_root_node
def test_attach_and_detach_share_the_root_node(tmp_path) -> None:
    '''Attach inserts a later visit. A second attach does not replace the file.'''

    path = _write_normative(tmp_path)
    attach_test(
        'domain/test_error',
        'test_error',
        'error_message_format',
        base_dir=tmp_path,
    )
    text = path.read_text()

    # The root test stays, gains its anchor, and is aliased under the tester.
    assert 'error_message_format: &error_message_format' in text
    assert 'error_message_format: *error_message_format' in text
    assert 'construction_derives_error_code' in text
    before = path.read_bytes()
    _assert_error(
        lambda: attach_test(
            'domain/test_error',
            'test_error',
            'error_message_format',
            base_dir=tmp_path,
        ),
        'TEST_ARTIFACT_ALREADY_EXISTS',
    )
    assert path.read_bytes() == before

    # Detach drops only the tester entry.
    detach_test(
        'domain/test_error',
        'test_error',
        'error_message_format',
        base_dir=tmp_path,
    )
    text = path.read_text()
    assert 'error_message_format: &error_message_format' in text
    assert 'error_message_format: *error_message_format' not in text

# ** test: remove_refuses_to_relocate_a_first_visit
def test_remove_refuses_to_relocate_a_first_visit(tmp_path) -> None:
    '''Removing an anchored fixture fails while an alias remains.'''

    path = _write_normative(tmp_path)
    before = path.read_bytes()
    _assert_error(
        lambda: remove_fixture('domain/test_error', 'error_message', base_dir=tmp_path),
        'TEST_ANCHOR_CONFLICT',
    )
    assert path.read_bytes() == before

    # Removing the later visit leaves the root anchor.
    remove_fixture(
        'domain/test_error',
        'error_message',
        tester='test_error',
        base_dir=tmp_path,
    )
    text = path.read_text()
    assert '&error_message' in text
    assert 'error_message: *error_message' not in text

# ** test: get_and_list_do_not_write
def test_get_and_list_do_not_write(tmp_path) -> None:
    '''Get of an alias returns the alias token. List keeps document order.'''

    path = _write_normative(tmp_path)
    before = path.read_bytes()
    got = get_fixture(
        'domain/test_error',
        'error_message',
        tester='test_error',
        base_dir=tmp_path,
    )

    # The alias is not inlined, and the two lists do not mix scopes.
    assert got['alias'] == 'error_message'
    assert got['fragment'] == '*error_message\n'
    assert 'class_name' not in got['fragment']
    assert list_fixtures('domain/test_error', base_dir=tmp_path) == [
        'error_message',
        'formatted_error_message',
    ]
    assert 'formatted_error_message' not in list_fixtures(
        'domain/test_error',
        tester='test_error',
        base_dir=tmp_path,
    )
    assert path.read_bytes() == before

# ** test: update_patches_without_replacing_the_node
def test_update_patches_without_replacing_the_node(tmp_path) -> None:
    '''A fixture patch leaves an existing merge. A tester container update fails.'''

    path = _write_normative(tmp_path)
    update_fixture(
        'domain/test_error',
        'formatted_error_message',
        payload={'attributes': {'lang': 'en_US'}},
        base_dir=tmp_path,
    )
    assert '<<: *error_message' in path.read_text()

    # Illegal updates do not replace the file.
    before = path.read_bytes()
    _assert_error(
        lambda: update_tester(
            'domain/test_error',
            'test_error',
            payload={'fixtures': {}},
            base_dir=tmp_path,
        ),
        'TEST_MODULE_WRITE_REFUSED',
    )
    _assert_error(
        lambda: update_fixture(
            'domain/test_error',
            'error_message',
            payload={'callback': lambda: None},
            base_dir=tmp_path,
        ),
        'TEST_MODULE_WRITE_REFUSED',
    )
    assert path.read_bytes() == before

# ** test: missing_and_illegal_addresses_do_not_create
def test_missing_and_illegal_addresses_do_not_create(tmp_path) -> None:
    '''A missing file, an illegal stem, and a variables root do not write.'''

    _assert_error(
        lambda: get_fixture('domain/test_missing', 'error_message', base_dir=tmp_path),
        'TEST_MODULE_NOT_FOUND',
    )
    assert not (tmp_path / 'tiferet_tests').exists()
    _assert_error(
        lambda: get_fixture('../config', 'error_message', base_dir=tmp_path),
        'TEST_MODULE_PATH_INVALID',
    )
    _assert_error(
        lambda: get_fixture('config', 'error_message', base_dir=tmp_path),
        'TEST_MODULE_PATH_INVALID',
    )

    # An illegal root is refused and left byte-for-byte.
    path = tmp_path / 'tiferet_tests' / 'domain' / 'test_vars.yml'
    path.parent.mkdir(parents=True)
    path.write_bytes(b'variables:\n  a: 1\n')
    before = path.read_bytes()
    _assert_error(
        lambda: update_fixture(
            'domain/test_vars',
            'a',
            payload={'b': 1},
            base_dir=tmp_path,
        ),
        'TEST_MODULE_WRITE_REFUSED',
    )
    assert path.read_bytes() == before

# ** test: no_writer_modules_are_added
def test_no_writer_modules_are_added() -> None:
    '''This writer adds neither a tester service stack nor a test mapper.'''

    root = Path(__file__).parents[2] / 'tiferet'
    assert not (root / 'events' / 'tester.py').exists()
    assert not (root / 'interfaces' / 'tester.py').exists()
    assert not (root / 'mappers' / 'tester.py').exists()
    assert not (root / 'repos' / 'tester.py').exists()
    assert not (root / 'events' / 'tester.py').exists()
    assert not (root / 'tiferet_tests').exists()
