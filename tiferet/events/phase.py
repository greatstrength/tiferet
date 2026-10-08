"""Tiferet Phase Harness Procedures"""

# *** imports

# ** infra
from pydantic import Field

# ** app
from ..domain import (
    INVALID_MODEL_ATTRIBUTE_ID,
    INVALID_MODEL_VALUE_ID,
    DomainObject,
    ModelError,
)
from ..mappers.core import Aggregate, TransferObject

# *** functions

# ** function: run_mapper_contract
def run_mapper_contract(exclude: list | None = None) -> None:
    '''
    Run the Aggregate and TransferObject base protocol.

    Contexts cannot import mappers. This function lives here so the phase
    dialect can call it without that edge. The harness owns the two bases.
    An exclude list is compared as a set. There is no YAML set.

    :param exclude: Names the to_data role excludes. Compared as a set.
    :type exclude: list | None
    :return: None.
    :rtype: None
    '''

    # Compare the exclude list as a set. Duplicates collapse.
    excluded = set(exclude or [])

    # The harness owns the aggregate base.
    class TestAggregate(Aggregate):
        '''Harness aggregate for the mapper contract.'''

        id: str = Field(
            ...,
            description='The identifier.',
        )

        name: str = Field(
            ...,
            description='The name.',
        )

    # The harness owns the transfer-object base.
    class TestDataObject(TransferObject):
        '''Harness transfer object for the mapper contract.'''

        _ROLES = {
            'to_data': {
                'exclude': excluded,
            },
            'to_model': {},
        }

        id: str = Field(
            ...,
            description='The identifier.',
        )

        name: str = Field(
            ...,
            description='The name.',
        )

    # The source model is a domain object the transfer object can copy.
    class SourceModel(DomainObject):
        '''Harness source model for from_model.'''

        id: str = Field(
            ...,
            description='The identifier.',
        )

        name: str = Field(
            ...,
            description='The name.',
        )

    # Construction.
    aggregate = TestAggregate(id='test_id', name='Test Aggregate')
    assert aggregate.id == 'test_id'
    assert aggregate.name == 'Test Aggregate'

    # set_attribute writes a known field.
    aggregate.set_attribute('name', 'Updated Name')
    assert aggregate.name == 'Updated Name'

    # An unknown attribute is INVALID_MODEL_ATTRIBUTE.
    try:
        aggregate.set_attribute('invalid_attribute', 'value')
    except ModelError as error:
        assert error.error_code == INVALID_MODEL_ATTRIBUTE_ID
    else:
        raise AssertionError('Unknown attribute should fail.')

    # An invalid value is INVALID_MODEL_VALUE.
    try:
        aggregate.set_attribute('name', ['not', 'a', 'string'])
    except ModelError as error:
        assert error.error_code == INVALID_MODEL_VALUE_ID
    else:
        raise AssertionError('Invalid value should fail.')

    # model_validate builds the transfer object from data.
    validated = TestDataObject.model_validate({
        'id': 'test_id',
        'name': 'Test Data',
    })
    assert isinstance(validated, TestDataObject)
    assert validated.name == 'Test Data'

    # from_model copies a domain object.
    source = SourceModel(id='test_id', name='Test Model')
    copied = TestDataObject.from_model(source)
    assert isinstance(copied, TestDataObject)
    assert copied.id == 'test_id'
    assert copied.name == 'Test Model'

    # map returns the aggregate class.
    mapped = copied.map(TestAggregate)
    assert isinstance(mapped, TestAggregate)
    assert mapped.id == 'test_id'

    # The exclude list is a set, not a YAML set.
    assert set(TestDataObject._ROLES['to_data']['exclude']) == excluded
    data_object = TestDataObject(id='test_id', name='Test Data')

    # to_data omits the excluded names.
    to_data = data_object.to_primitive(role='to_data')
    for name in excluded:
        assert name not in to_data
    if 'id' not in excluded:
        assert to_data['id'] == 'test_id'
    if 'name' not in excluded:
        assert to_data['name'] == 'Test Data'

    # to_model includes the fields.
    to_model = data_object.to_primitive(role='to_model')
    assert to_model['id'] == 'test_id'
    assert to_model['name'] == 'Test Data'

    # An unknown role falls back to the default dump.
    fallback = data_object.to_primitive(role='unknown_role')
    assert fallback['id'] == 'test_id'
    assert fallback['name'] == 'Test Data'
