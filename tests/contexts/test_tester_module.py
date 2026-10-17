"""Tiferet Test Module Context Tests"""

# *** imports

# ** core
from pathlib import Path

# ** infra
import pytest

# ** app
from tiferet import use_tester
from tiferet.assets import TiferetError
from tiferet.contexts.core import BaseContext
from tiferet.contexts.tester_module import TestModuleContext
from tiferet.domain.tester_module import TestModuleAddress, TestModuleDocument

# *** fixtures

# ** fixture: tmp_dir
@pytest.fixture
def tmp_dir(tmp_path: Path) -> Path:
    '''
    Provide a writable temporary directory.

    :param tmp_path: The pytest temporary path fixture.
    :type tmp_path: Path
    :return: The writable temporary directory.
    :rtype: Path
    '''

    # Return the pytest temporary directory.
    return tmp_path

# *** testers

# ** tester: test_test_module_context
@use_tester(
    type='context',
    target_cls=TestModuleContext,
    domain_cls=TestModuleDocument,
    from_domain_cases=[
        {
            'data': {
                'address': {
                    'rel': 'contexts/test_tester_module',
                    'base_dir': '.',
                    'path': '/unused/tiferet_tests/contexts/test_tester_module.yml',
                },
            },
        },
    ],
    domain_type_cases=[
        {
            'declares': True,
        },
    ],
    for_domain_cases=[
        {
            'domain_module_path': 'tiferet.domain.tester_module',
            'domain_class_name': 'TestModuleDocument',
            'context_module_path': 'tiferet.contexts.tester_module',
            'context_class_name': 'TestModuleContext',
        },
    ],
)
class TestTestModuleContext:
    '''
    Tests for TestModuleContext.
    '''

    # * test: test_module_from_domain_binds_the_domain
    def test_module_from_domain_binds_the_domain(self, test_ctx) -> None:
        '''
        Assert from_domain binds TestModuleContext to the constructed document.

        :param test_ctx: The bound context tester context.
        :type test_ctx: ContextTesterContext
        :return: None
        :rtype: None
        '''

        # Assert from_domain cases bind the target context and domain identity.
        test_ctx.assert_from_domain()

    # * test: test_module_domain_type_is_own_namespace
    def test_module_domain_type_is_own_namespace(self, test_ctx) -> None:
        '''
        Assert domain_type is own-namespace TestModuleDocument.

        :param test_ctx: The bound context tester context.
        :type test_ctx: ContextTesterContext
        :return: None
        :rtype: None
        '''

        # Assert domain_type is declared on TestModuleContext as TestModuleDocument.
        test_ctx.assert_domain_type()

    # * test: test_module_for_domain
    def test_module_for_domain(self, test_ctx) -> None:
        '''
        Assert BaseContext.for_domain resolves TestModuleContext.

        :param test_ctx: The bound context tester context.
        :type test_ctx: ContextTesterContext
        :return: None
        :rtype: None
        '''

        # Assert the registry mapping for TestModuleDocument.
        test_ctx.assert_for_domain()

    # * test: from_domain_leaves_working_null
    def test_from_domain_leaves_working_null(self) -> None:
        '''
        Assert from_domain leaves working null when body is set.

        :return: None
        :rtype: None
        '''

        # Construct a document whose body is a fixtures mapping.
        document = TestModuleDocument(
            address={
                'rel': 'contexts/test_tester_module',
                'base_dir': '.',
                'path': '/unused/tiferet_tests/contexts/test_tester_module.yml',
            },
            body={
                'fixtures': {},
            },
        )

        # Bind via from_domain and assert working stays null.
        context = TestModuleContext.from_domain(document)
        assert context.working is None

    # * test: bind_sets_working_to_document_body
    def test_bind_sets_working_to_document_body(self) -> None:
        '''
        Assert bind sets working to the document body identity.

        :return: None
        :rtype: None
        '''

        # Construct a document whose body is a fixtures mapping.
        body = {
            'fixtures': {},
        }
        document = TestModuleDocument(
            address={
                'rel': 'contexts/test_tester_module',
                'base_dir': '.',
                'path': '/unused/tiferet_tests/contexts/test_tester_module.yml',
            },
            body=body,
        )

        # Bind and assert working and domain identities.
        context = TestModuleContext.bind(document)
        assert context.working is body
        assert context.domain is document

    # * test: bind_with_null_body_leaves_working_null
    def test_bind_with_null_body_leaves_working_null(self) -> None:
        '''
        Assert bind leaves working null when body is null.

        :return: None
        :rtype: None
        '''

        # Construct a document with a null body.
        document = TestModuleDocument(
            address={
                'rel': 'contexts/test_tester_module',
                'base_dir': '.',
                'path': '/unused/tiferet_tests/contexts/test_tester_module.yml',
            },
            body=None,
        )

        # Bind and assert working is null.
        context = TestModuleContext.bind(document)
        assert context.working is None

    # * test: address_resolves_a_nested_stem
    def test_address_resolves_a_nested_stem(self, tmp_dir: Path) -> None:
        '''
        Assert _address resolves a nested stem under tiferet_tests.

        :param tmp_dir: A writable temporary directory.
        :type tmp_dir: Path
        :return: None
        :rtype: None
        '''

        # Resolve a nested stem against the temporary base.
        address = TestModuleContext._address(
            'contexts/test_tester_module',
            base_dir=str(tmp_dir),
        )

        # Assert address type and fields.
        assert isinstance(address, TestModuleAddress)
        assert address.rel == 'contexts/test_tester_module'
        assert address.base_dir == str(tmp_dir)
        expected = (tmp_dir / 'tiferet_tests' / 'contexts' / 'test_tester_module.yml').resolve()
        assert address.path == str(expected)

    # * test: address_resolves_a_single_segment_stem
    def test_address_resolves_a_single_segment_stem(self, tmp_dir: Path) -> None:
        '''
        Assert _address resolves a single-segment stem.

        :param tmp_dir: A writable temporary directory.
        :type tmp_dir: Path
        :return: None
        :rtype: None
        '''

        # Resolve a single-segment stem against the temporary base.
        address = TestModuleContext._address(
            'test_foo',
            base_dir=str(tmp_dir),
        )

        # Assert address fields.
        assert address.rel == 'test_foo'
        assert address.base_dir == str(tmp_dir)
        expected = (tmp_dir / 'tiferet_tests' / 'test_foo.yml').resolve()
        assert address.path == str(expected)

    # * test: address_accepts_a_path_base_dir
    def test_address_accepts_a_path_base_dir(self, tmp_dir: Path) -> None:
        '''
        Assert _address accepts a Path base_dir and stores its str form.

        :param tmp_dir: A writable temporary directory.
        :type tmp_dir: Path
        :return: None
        :rtype: None
        '''

        # Resolve with a Path base_dir object.
        address = TestModuleContext._address(
            'domain/test_error',
            base_dir=tmp_dir,
        )

        # Assert address fields use the string form of base_dir.
        assert address.rel == 'domain/test_error'
        assert address.base_dir == str(tmp_dir)
        expected = (tmp_dir / 'tiferet_tests' / 'domain' / 'test_error.yml').resolve()
        assert address.path == str(expected)

    # * test: address_rejects_a_non_string_rel
    def test_address_rejects_a_non_string_rel(self) -> None:
        '''
        Assert _address rejects a non-string rel.

        :return: None
        :rtype: None
        '''

        # Refuse a non-string rel with the relative-stem message.
        with pytest.raises(TiferetError, match='A test module address must be a relative stem.'):
            TestModuleContext._address(1)

    # * test: address_rejects_a_non_path_base_dir
    def test_address_rejects_a_non_path_base_dir(self) -> None:
        '''
        Assert _address rejects a non-str, non-Path base_dir.

        :return: None
        :rtype: None
        '''

        # Refuse a non-path base_dir with the relative-stem message.
        with pytest.raises(TiferetError, match='A test module address must be a relative stem.'):
            TestModuleContext._address('test_foo', base_dir=1)

    # * test: address_rejects_an_empty_rel
    def test_address_rejects_an_empty_rel(self) -> None:
        '''
        Assert _address rejects an empty rel.

        :return: None
        :rtype: None
        '''

        # Refuse an empty rel with the illegal message.
        with pytest.raises(TiferetError, match='A test module address is illegal.'):
            TestModuleContext._address('')

    # * test: address_rejects_an_unstripped_rel
    def test_address_rejects_an_unstripped_rel(self) -> None:
        '''
        Assert _address rejects an unstripped rel.

        :return: None
        :rtype: None
        '''

        # Refuse an unstripped rel with the illegal message.
        with pytest.raises(TiferetError, match='A test module address is illegal.'):
            TestModuleContext._address(' test_foo')

    # * test: address_rejects_an_absolute_rel
    def test_address_rejects_an_absolute_rel(self) -> None:
        '''
        Assert _address rejects an absolute rel.

        :return: None
        :rtype: None
        '''

        # Refuse an absolute rel with the illegal message.
        with pytest.raises(TiferetError, match='A test module address is illegal.'):
            TestModuleContext._address('/test_foo')

    # * test: address_rejects_a_backslash
    def test_address_rejects_a_backslash(self) -> None:
        '''
        Assert _address rejects a backslash in rel.

        :return: None
        :rtype: None
        '''

        # Refuse a backslash rel with the illegal message.
        with pytest.raises(TiferetError, match='A test module address is illegal.'):
            TestModuleContext._address('contexts\\test_foo')

    # * test: address_rejects_dotdot
    def test_address_rejects_dotdot(self) -> None:
        '''
        Assert _address rejects a .. segment in rel.

        :return: None
        :rtype: None
        '''

        # Refuse a dotdot rel with the illegal message.
        with pytest.raises(TiferetError, match='A test module address is illegal.'):
            TestModuleContext._address('../test_foo')

    # * test: address_rejects_the_tests_prefix
    def test_address_rejects_the_tests_prefix(self) -> None:
        '''
        Assert _address rejects the tests/ prefix.

        :return: None
        :rtype: None
        '''

        # Refuse the tests/ prefix with the illegal message.
        with pytest.raises(TiferetError, match='A test module address is illegal.'):
            TestModuleContext._address('tests/test_foo')

    # * test: address_rejects_the_tests_int_prefix
    def test_address_rejects_the_tests_int_prefix(self) -> None:
        '''
        Assert _address rejects the tests_int/ prefix.

        :return: None
        :rtype: None
        '''

        # Refuse the tests_int/ prefix with the illegal message.
        with pytest.raises(TiferetError, match='A test module address is illegal.'):
            TestModuleContext._address('tests_int/test_foo')

    # * test: address_rejects_the_tiferet_tests_prefix
    def test_address_rejects_the_tiferet_tests_prefix(self) -> None:
        '''
        Assert _address rejects the tiferet_tests/ prefix.

        :return: None
        :rtype: None
        '''

        # Refuse the tiferet_tests/ prefix with the illegal message.
        with pytest.raises(TiferetError, match='A test module address is illegal.'):
            TestModuleContext._address('tiferet_tests/test_foo')

    # * test: address_rejects_a_py_token
    def test_address_rejects_a_py_token(self) -> None:
        '''
        Assert _address rejects a .py token in rel.

        :return: None
        :rtype: None
        '''

        # Refuse a .py token with the illegal message.
        with pytest.raises(TiferetError, match='A test module address is illegal.'):
            TestModuleContext._address('domain/test_foo.py')

    # * test: address_rejects_a_yml_token
    def test_address_rejects_a_yml_token(self) -> None:
        '''
        Assert _address rejects a .yml token in rel.

        :return: None
        :rtype: None
        '''

        # Refuse a .yml token with the illegal message.
        with pytest.raises(TiferetError, match='A test module address is illegal.'):
            TestModuleContext._address('domain/test_foo.yml')

    # * test: address_rejects_a_yaml_token
    def test_address_rejects_a_yaml_token(self) -> None:
        '''
        Assert _address rejects a .yaml token in rel.

        :return: None
        :rtype: None
        '''

        # Refuse a .yaml token with the illegal message.
        with pytest.raises(TiferetError, match='A test module address is illegal.'):
            TestModuleContext._address('domain/test_foo.yaml')

    # * test: address_rejects_an_invalid_segment
    def test_address_rejects_an_invalid_segment(self) -> None:
        '''
        Assert _address rejects a segment that fails the name pattern.

        :return: None
        :rtype: None
        '''

        # Refuse an invalid segment with the illegal message.
        with pytest.raises(TiferetError, match='A test module address is illegal.'):
            TestModuleContext._address('Domain/test_foo')

    # * test: address_rejects_a_stem_without_the_test_prefix
    def test_address_rejects_a_stem_without_the_test_prefix(self) -> None:
        '''
        Assert _address rejects a stem without the test_ prefix.

        :return: None
        :rtype: None
        '''

        # Refuse a stem without the test_ prefix.
        with pytest.raises(TiferetError, match=r'A test module stem must match test_\*\.'):
            TestModuleContext._address('config')

    # * test: address_rejects_a_symlink_escape
    def test_address_rejects_a_symlink_escape(self, tmp_dir: Path) -> None:
        '''
        Assert _address rejects a path that escapes tiferet_tests via symlink.

        :param tmp_dir: A writable temporary directory.
        :type tmp_dir: Path
        :return: None
        :rtype: None
        '''

        # Create tiferet_tests with a symlink that points outside tmp_dir.
        tests_root = tmp_dir / 'tiferet_tests'
        tests_root.mkdir()
        outside = tmp_dir.parent / f'{tmp_dir.name}-outside'
        outside.mkdir(exist_ok=True)
        link = tests_root / 'outside'
        link.symlink_to(outside)

        # Refuse the symlink escape with the stay-under message.
        with pytest.raises(TiferetError, match='A test module path must stay under tiferet_tests.'):
            TestModuleContext._address(
                'outside/test_foo',
                base_dir=str(tmp_dir),
            )
