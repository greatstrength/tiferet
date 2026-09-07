"""Tiferet Tester Event Tests"""

# *** imports

# ** infra
from unittest import mock

# ** app
from tiferet.events.core import DomainEvent
from tiferet.events.tester import (
    AddTester,
    GetTester,
    ListTesters,
    RemoveTester,
    UpdateTester,
)
from tiferet.interfaces import TesterService
from tiferet.mappers import TesterAggregate

# *** functions

# ** function: build_tester
def build_tester() -> TesterAggregate:
    '''Build a representative aggregate tester.

    :return: The tester aggregate.
    :rtype: TesterAggregate
    '''

    # Return a mutable aggregate tester.
    return TesterAggregate(
        id='aggregate.ErrorAggregate',
        type='aggregate',
        module_path='tiferet.mappers.error',
        class_name='ErrorAggregate',
        sample_data={'id': 'TEST'},
        set_attribute_params=[],
    )

# *** tests

# ** test: tester_events
def test_tester_events_via_domain_event_handle():
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
    tester = build_tester()
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
