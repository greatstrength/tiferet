"""Tiferet Tester Event Tests"""

# *** imports

# ** infra
import pytest
from unittest import mock

# ** app
from tiferet.assets import TiferetError
from tiferet.assets.error import INVALID_TESTER_TYPE_ID
from tiferet.events.core import DomainEvent
from tiferet.events.tester import (
    AddTester,
    GetTester,
    ListTesters,
    RemoveTester,
    UpdateTester,
)
from tiferet.interfaces import TesterService
from tiferet.mappers import TesterAggregate as ComponentTester

# *** fixtures

# ** fixture: tester
@pytest.fixture
def tester() -> ComponentTester:
    '''Build a representative aggregate tester.

    :return: The tester aggregate.
    :rtype: TesterAggregate
    '''

    # Return a mutable aggregate tester.
    return ComponentTester(
        id='aggregate.ErrorAggregate',
        type='aggregate',
        module_path='tiferet.mappers.error',
        class_name='ErrorAggregate',
        sample_data={'id': 'TEST'},
        set_attribute_params=[],
    )

# *** tests

# ** test: tester_events
def test_tester_events_via_domain_event_handle(tester):
    '''Test all tester events through the standard DomainEvent entry point.'''

    # Add a tester after a no-collision response.
    service = mock.Mock(spec=TesterService)
    service.exists.return_value = False
    added = DomainEvent.handle(
        AddTester,
        dependencies={'tester_service': service},
        id='aggregate.NewAggregate',
        type='aggregate',
        module_path='tiferet.mappers.error',
        class_name='ErrorAggregate',
    )
    assert added.id == 'aggregate.NewAggregate'
    service.save.assert_called_once_with(added)

    # Resolve a configured tester, then list it with the type filter.
    service.get.return_value = tester
    assert DomainEvent.handle(
        GetTester,
        dependencies={'tester_service': service},
        id=tester.id,
    ) is tester
    service.list.return_value = [tester]
    assert DomainEvent.handle(
        ListTesters,
        dependencies={'tester_service': service},
        type='aggregate',
    ) == [tester]
    service.list.assert_called_with(type='aggregate')

    # Update sample data through the aggregate-specific mutation path.
    updated = DomainEvent.handle(
        UpdateTester,
        dependencies={'tester_service': service},
        id=tester.id,
        attribute='sample_data',
        value={'name': 'Updated'},
    )
    assert updated.sample_data['name'] == 'Updated'

    # Remove the tester through the idempotent event.
    assert DomainEvent.handle(
        RemoveTester,
        dependencies={'tester_service': service},
        id=tester.id,
    ) == tester.id
    service.delete.assert_called_once_with(tester.id)

# ** test: add_tester_rejects_invalid_type
def test_add_tester_rejects_invalid_type() -> None:
    '''Test AddTester raises catalogued INVALID_TESTER_TYPE before mapping.'''

    # Invoke AddTester with an unrecognized discriminator.
    service = mock.Mock(spec=TesterService)
    with pytest.raises(TiferetError) as exc_info:
        DomainEvent.handle(
            AddTester,
            dependencies={'tester_service': service},
            id='unknown.Tester',
            type='unknown',
            module_path='tiferet.mappers.error',
            class_name='ErrorAggregate',
        )

    # Assert the catalogued type error is raised before persistence.
    assert exc_info.value.error_code == INVALID_TESTER_TYPE_ID
    service.save.assert_not_called()
