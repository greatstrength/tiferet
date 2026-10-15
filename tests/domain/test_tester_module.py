"""Tests for Tiferet Test Module Domain Models"""

# *** imports

# ** infra
import pytest
from pydantic import ValidationError

# ** app
from tiferet import use_tester
from tiferet.domain import TestModuleAddress, TestModuleDocument

# *** fixtures

# ** fixture: address_data
@pytest.fixture
def address_data() -> dict:
    '''
    Sample TestModuleAddress field mapping.

    :return: The address field mapping.
    :rtype: dict
    '''

    # Return the catalog address literals.
    return {
        'rel': 'domain/test_sample',
        'base_dir': '.',
        'path': 'tiferet_tests/domain/test_sample.yml',
    }

# ** fixture: document_data
@pytest.fixture
def document_data(address_data: dict) -> dict:
    '''
    Sample TestModuleDocument field mapping.

    :param address_data: The sample address field mapping.
    :type address_data: dict
    :return: The document field mapping.
    :rtype: dict
    '''

    # Return the catalog document literals, using the address fixture.
    return {
        'address': address_data,
        'text': 'name: sample\n',
        'body': {
            'name': 'composed',
        },
        'mapping': {
            'name': 'plain',
        },
    }

# *** tests

# ** test: domain_exports_test_module_models
def test_domain_exports_test_module_models() -> None:
    '''
    Test that the domain package exports the test-module models before Request.
    '''

    # Import the package and the owning module for identity checks.
    import tiferet.domain as domain
    import tiferet.domain.tester_module as tester_module

    # Assert the export order immediately before Request.
    names = list(domain.__all__)
    request_at = names.index('Request')
    assert names[request_at - 2] == 'TestModuleAddress'
    assert names[request_at - 1] == 'TestModuleDocument'

    # Assert each exported attribute is the class from tester_module.
    assert domain.TestModuleAddress is tester_module.TestModuleAddress
    assert domain.TestModuleDocument is tester_module.TestModuleDocument

# *** testers

# ** tester: test_test_module_address
@use_tester(
    type='domain',
    target_cls=TestModuleAddress,
    sample_data={
        'rel': 'domain/test_sample',
        'base_dir': '.',
        'path': 'tiferet_tests/domain/test_sample.yml',
    },
    equality_fields=[
        'rel',
        'base_dir',
        'path',
    ],
)
class TestTestModuleAddress:
    '''
    Tests for TestModuleAddress.
    '''

    # * test: test_module_address_new
    def test_module_address_new(self, test_ctx, address_data: dict) -> None:
        '''
        Construct from sample data and assert the address fields.

        :param test_ctx: The bound domain tester context.
        :type test_ctx: DomainTesterContext
        :param address_data: The sample address field mapping.
        :type address_data: dict
        '''

        # Assert construction against the tester sample.
        test_ctx.assert_new()

        # Assert the constructed fields equal the address fixture.
        address = test_ctx.make_target()
        assert isinstance(address, TestModuleAddress)
        assert address.rel == address_data['rel']
        assert address.base_dir == address_data['base_dir']
        assert address.path == address_data['path']

    # * test: test_module_address_rejects_extra
    def test_module_address_rejects_extra(self, address_data: dict) -> None:
        '''
        Reject construction with an unknown key.

        :param address_data: The sample address field mapping.
        :type address_data: dict
        '''

        # Construct with an extra key and expect ValidationError.
        with pytest.raises(ValidationError, match='extra'):
            TestModuleAddress(**address_data, extra='nope')

    # * test: test_module_address_is_frozen
    def test_module_address_is_frozen(self, address_data: dict) -> None:
        '''
        Reject assignment after construction.

        :param address_data: The sample address field mapping.
        :type address_data: dict
        '''

        # Construct an address and assign rel after construction.
        address = TestModuleAddress(**address_data)
        with pytest.raises(ValidationError, match='Instance is frozen'):
            address.rel = 'other'

    # * test: test_module_address_declares_frozen
    def test_module_address_declares_frozen(self) -> None:
        '''
        Read the class's own-namespace frozen declaration.
        '''

        # Assert model_config is declared on TestModuleAddress and frozen.
        assert 'model_config' in TestModuleAddress.__dict__
        assert TestModuleAddress.__dict__['model_config']['frozen'] is True

# ** tester: test_test_module_document
@use_tester(
    type='domain',
    target_cls=TestModuleDocument,
    sample_data={
        'address': {
            'rel': 'domain/test_sample',
            'base_dir': '.',
            'path': 'tiferet_tests/domain/test_sample.yml',
        },
        'text': 'name: sample\n',
        'body': {
            'name': 'composed',
        },
        'mapping': {
            'name': 'plain',
        },
    },
    equality_fields=[
        'text',
        'body',
        'mapping',
    ],
)
class TestTestModuleDocument:
    '''
    Tests for TestModuleDocument.
    '''

    # * test: test_module_document_new
    def test_module_document_new(self, test_ctx, document_data: dict) -> None:
        '''
        Construct from sample data and assert document fields.

        :param test_ctx: The bound domain tester context.
        :type test_ctx: DomainTesterContext
        :param document_data: The sample document field mapping.
        :type document_data: dict
        '''

        # Assert construction against the tester sample.
        test_ctx.assert_new()

        # Assert address type and fields, plus stored document values.
        document = test_ctx.make_target()
        assert isinstance(document, TestModuleDocument)
        assert document.text == document_data['text']
        assert document.body == document_data['body']
        assert document.mapping == document_data['mapping']
        assert isinstance(document.address, TestModuleAddress)
        assert document.address.rel == document_data['address']['rel']
        assert document.address.base_dir == document_data['address']['base_dir']
        assert document.address.path == document_data['address']['path']

    # * test: test_module_document_defaults_optional
    def test_module_document_defaults_optional(self, address_data: dict) -> None:
        '''
        Default optional fields when only an address is supplied.

        :param address_data: The sample address field mapping.
        :type address_data: dict
        '''

        # Construct a document with only the address mapping.
        document = TestModuleDocument(address=address_data)

        # Assert optional fields default to None.
        assert document.text is None
        assert document.body is None
        assert document.mapping is None

    # * test: test_module_document_rejects_extra
    def test_module_document_rejects_extra(self, address_data: dict) -> None:
        '''
        Reject construction with an unknown key.

        :param address_data: The sample address field mapping.
        :type address_data: dict
        '''

        # Construct with an extra key and expect ValidationError.
        with pytest.raises(ValidationError, match='extra'):
            TestModuleDocument(address=address_data, extra='nope')

    # * test: test_module_document_is_frozen
    def test_module_document_is_frozen(self, document_data: dict) -> None:
        '''
        Reject assignment after construction.

        :param document_data: The sample document field mapping.
        :type document_data: dict
        '''

        # Construct a document and assign text after construction.
        document = TestModuleDocument(**document_data)
        with pytest.raises(ValidationError, match='Instance is frozen'):
            document.text = 'other'

    # * test: test_module_document_address_identity
    def test_module_document_address_identity(self, address_data: dict) -> None:
        '''
        Keep the supplied address instance on the document.

        :param address_data: The sample address field mapping.
        :type address_data: dict
        '''

        # Construct an address, then a document that holds it.
        address = TestModuleAddress(**address_data)
        document = TestModuleDocument(address=address)

        # Assert address fields equal the fixture and identity is preserved.
        assert document.address.rel == address_data['rel']
        assert document.address.base_dir == address_data['base_dir']
        assert document.address.path == address_data['path']
        assert document.address is address

    # * test: test_module_document_declares_frozen
    def test_module_document_declares_frozen(self) -> None:
        '''
        Read the class's own-namespace frozen declaration.
        '''

        # Assert model_config is declared on TestModuleDocument and frozen.
        assert 'model_config' in TestModuleDocument.__dict__
        assert TestModuleDocument.__dict__['model_config']['frozen'] is True
