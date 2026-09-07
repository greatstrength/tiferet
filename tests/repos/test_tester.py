"""Tiferet Tester Configuration Repository Tests"""

# *** imports

# ** infra
import pytest
import yaml

# ** app
from tiferet.mappers import TesterAggregate as ComponentTester
from tiferet.repos.tester import TesterConfigRepository as ComponentTesterRepository

# *** constants

# ** constant: tester_data
TESTER_DATA = {
    'testers': {
        'domain.ErrorMessage': {
            'type': 'domain',
            'module_path': 'tiferet.domain.error',
            'class_name': 'ErrorMessage',
            'sample_data': {'lang': 'en_US', 'text': 'Test'},
            'description_cases': [],
        },
        'aggregate.ErrorAggregate': {
            'type': 'aggregate',
            'module_path': 'tiferet.mappers.error',
            'class_name': 'ErrorAggregate',
            'sample_data': {'id': 'TEST', 'name': 'Test', 'message': []},
            'set_attribute_params': [],
        },
    },
}

# *** fixtures

# ** fixture: tester_config_repo
@pytest.fixture
def tester_config_repo(tmp_path) -> ComponentTesterRepository:
    '''Create a repository backed by temporary tester configuration.

    :param tmp_path: Pytest temporary path fixture.
    :type tmp_path: object
    :return: The configured tester repository.
    :rtype: TesterConfigRepository
    '''

    # Persist the sample flat tester configuration.
    config_file = tmp_path / 'testers.yml'
    with open(config_file, 'w', encoding='utf-8') as config_stream:
        yaml.safe_dump(TESTER_DATA, config_stream)
    return ComponentTesterRepository(str(config_file))

# *** tests

# ** test_int: tester_config_repository_five_methods
def test_int_tester_config_repository_five_methods(tester_config_repo):
    '''Test exists, get, list, save, and idempotent delete.'''

    # Check lookup and flat-section retrieval.
    assert tester_config_repo.exists('domain.ErrorMessage')
    assert not tester_config_repo.exists('missing')
    aggregate = tester_config_repo.get('aggregate.ErrorAggregate')
    assert aggregate.id == 'aggregate.ErrorAggregate'
    assert tester_config_repo.get('missing') is None

    # Check all entries and a discriminator-filtered result.
    assert len(tester_config_repo.list()) == 2
    assert [tester.id for tester in tester_config_repo.list(type='domain')] == [
        'domain.ErrorMessage',
    ]

    # Save a third entry and confirm it is retrieved from configuration.
    tester_config_repo.save(
        ComponentTester(
            id='aggregate.NewAggregate',
            type='aggregate',
            module_path='tiferet.mappers.error',
            class_name='ErrorAggregate',
            sample_data={},
            set_attribute_params=[],
        ),
    )
    assert tester_config_repo.get('aggregate.NewAggregate').class_name == 'ErrorAggregate'

    # Delete twice to verify idempotent removal.
    tester_config_repo.delete('aggregate.NewAggregate')
    tester_config_repo.delete('aggregate.NewAggregate')
    assert tester_config_repo.get('aggregate.NewAggregate') is None
