"""Tiferet Tester Events"""

# *** imports

# ** core
from typing import Any, Dict, List

# ** app
from ..interfaces import TesterService
from ..mappers import TesterAggregate
from .core import DomainEvent, a

# *** events

# ** event: tester_event
class TesterEvent(DomainEvent):
    '''Base event holding the shared TesterService dependency.'''

    # * attribute: tester_service
    tester_service: TesterService

    # * init
    def __init__(self, tester_service: TesterService) -> None:
        '''Initialize the tester event.

        :param tester_service: The tester service dependency.
        :type tester_service: TesterService
        '''

        # Set the shared service dependency.
        self.tester_service = tester_service

# ** event: add_tester
class AddTester(TesterEvent):
    '''Create and persist a declarative tester configuration.'''

    # * method: execute
    @DomainEvent.parameters_required(['id', 'type', 'module_path', 'class_name'])
    def execute(
            self,
            id: str,
            type: str,
            module_path: str,
            class_name: str,
            **kwargs,
        ) -> TesterAggregate:
        '''Add a tester with its target type reference.

        :param id: The tester identifier.
        :type id: str
        :param type: The tester discriminator.
        :type type: str
        :param module_path: The target module path.
        :type module_path: str
        :param class_name: The target class name.
        :type class_name: str
        :param kwargs: Additional variant-specific fields.
        :type kwargs: dict
        :return: The created tester aggregate.
        :rtype: TesterAggregate
        '''

        # Reject unrecognized tester discriminators before config construction.
        self.verify(
            expression=type in (
                'domain',
                'aggregate',
                'transfer_object',
                'domain_event',
                'service_event',
                'generic',
            ),
            error_code=a.error.INVALID_TESTER_TYPE_ID,
            type=type,
        )

        # Dispatch the supplied data to its tester variant.
        tester = TesterAggregate.build_config_object(
            {
                'id': id,
                'type': type,
                'module_path': module_path,
                'class_name': class_name,
                **kwargs,
            },
        ).map()

        # Reject a collision before writing the new configuration.
        self.verify(
            expression=not self.tester_service.exists(tester.id),
            error_code=a.error.TESTER_ALREADY_EXISTS_ID,
            id=tester.id,
        )
        self.tester_service.save(tester)
        return tester

# ** event: get_tester
class GetTester(TesterEvent):
    '''Retrieve a tester with a supplied default-catalog fallback.'''

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(
            self,
            id: str,
            default_tester_index: Dict[str, Any] = {},
            **kwargs,
        ) -> TesterAggregate:
        '''Retrieve a tester by id.

        :param id: The tester identifier.
        :type id: str
        :param default_tester_index: Defaults used after a repository miss.
        :type default_tester_index: Dict[str, Any]
        :param kwargs: Additional event arguments.
        :type kwargs: dict
        :return: The resolved tester aggregate.
        :rtype: TesterAggregate
        '''

        # Check persisted configuration before the supplied default index.
        tester = self.tester_service.get(id) or (default_tester_index or {}).get(id)
        self.verify(
            expression=tester is not None,
            error_code=a.error.TESTER_NOT_FOUND_ID,
            id=id,
        )
        return tester

# ** event: list_testers
class ListTesters(TesterEvent):
    '''List configured testers within an optional type partition.'''

    # * method: execute
    def execute(self, type: str | None = None, **kwargs) -> List[TesterAggregate]:
        '''List configured tester aggregates.

        :param type: An optional tester discriminator filter.
        :type type: str | None
        :param kwargs: Additional event arguments.
        :type kwargs: dict
        :return: Matching tester aggregates.
        :rtype: List[TesterAggregate]
        '''

        # Delegate listing and filtering to the service.
        return self.tester_service.list(type=type)

# ** event: update_tester
class UpdateTester(TesterEvent):
    '''Update an allowed tester attribute and persist the result.'''

    # * method: execute
    @DomainEvent.parameters_required(['id', 'attribute'])
    def execute(
            self,
            id: str,
            attribute: str,
            value: Any,
            **kwargs,
        ) -> TesterAggregate:
        '''Update a tester's name, target, or sample data.

        :param id: The tester identifier.
        :type id: str
        :param attribute: The supported attribute name.
        :type attribute: str
        :param value: The new attribute value.
        :type value: Any
        :param kwargs: Additional event arguments.
        :type kwargs: dict
        :return: The updated tester aggregate.
        :rtype: TesterAggregate
        '''

        # Reject attributes outside the public tester mutation surface.
        self.verify(
            expression=attribute in (
                'module_path',
                'class_name',
                'sample_data',
            ),
            error_code=a.error.INVALID_TESTER_ATTRIBUTE_ID,
            attribute=attribute,
        )
        tester = self.tester_service.get(id)
        self.verify(
            expression=tester is not None,
            error_code=a.error.TESTER_NOT_FOUND_ID,
            id=id,
        )

        # Apply the target-aware mutation selected by attribute.
        if attribute == 'module_path':
            tester.retarget(value, tester.class_name)
        elif attribute == 'class_name':
            tester.retarget(tester.module_path, value)
        else:
            tester.set_sample_data(value)

        # Persist and return the changed aggregate.
        self.tester_service.save(tester)
        return tester

# ** event: remove_tester
class RemoveTester(TesterEvent):
    '''Remove a tester configuration idempotently.'''

    # * method: execute
    @DomainEvent.parameters_required(['id'])
    def execute(self, id: str, **kwargs) -> str:
        '''Remove a tester by identifier.

        :param id: The tester identifier.
        :type id: str
        :param kwargs: Additional event arguments.
        :type kwargs: dict
        :return: The removed identifier.
        :rtype: str
        '''

        # Delegate idempotent deletion to the service.
        self.tester_service.delete(id)
        return id
