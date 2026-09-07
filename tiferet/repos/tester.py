"""Tiferet Tester Configuration Repository"""

# *** imports

# ** core
from typing import List

# ** app
from ..interfaces import TesterService
from ..mappers import TesterAggregate
from .core import ConfigurationRepository

# *** repos

# ** repo: tester_config_repository
class TesterConfigRepository(TesterService, ConfigurationRepository):
    '''Configuration repository for flat, id-keyed tester definitions.'''

    # * init
    def __init__(self, tester_config: str, encoding: str = 'utf-8') -> None:
        '''Initialize the tester configuration repository.

        :param tester_config: The configuration file path.
        :type tester_config: str
        :param encoding: The file encoding.
        :type encoding: str
        '''

        # Initialize the format-agnostic repository base.
        ConfigurationRepository.__init__(
            self,
            config_file=tester_config,
            encoding=encoding,
        )

    # * method: exists
    def exists(self, id: str) -> bool:
        '''Check whether a tester exists.

        :param id: The tester identifier.
        :type id: str
        :return: True when the tester exists.
        :rtype: bool
        '''

        # Load the flat tester section and test the identifier.
        testers_data = self._load(
            start_node=lambda data: data.get('testers', {}),
        )
        return id in testers_data

    # * method: get
    def get(self, id: str) -> TesterAggregate | None:
        '''Retrieve a tester aggregate by id.

        :param id: The tester identifier.
        :type id: str
        :return: The aggregate, or None when absent.
        :rtype: TesterAggregate | None
        '''

        # Load the requested tester entry.
        tester_data = self._load(
            start_node=lambda data: data.get('testers', {}).get(id),
        )
        if not tester_data:
            return None

        # Dispatch to the matching config variant and map the aggregate.
        return TesterAggregate.build_config_object(
            {**tester_data, 'id': id},
        ).map()

    # * method: list
    def list(self, type: str | None = None) -> List[TesterAggregate]:
        '''List configured testers, optionally filtered by type.

        :param type: Optional tester discriminator filter.
        :type type: str | None
        :return: Matching tester aggregates.
        :rtype: List[TesterAggregate]
        '''

        # Map every flat config entry through the polymorphic dispatcher.
        testers_data = self._load(
            start_node=lambda data: data.get('testers', {}),
        )
        testers = [
            TesterAggregate.build_config_object(
                {**tester_data, 'id': tester_id},
            ).map()
            for tester_id, tester_data in testers_data.items()
        ]

        # Retain every entry, or only the requested type partition.
        return [
            tester
            for tester in testers
            if type is None or tester.type == type
        ]

    # * method: save
    def save(self, tester: TesterAggregate) -> None:
        '''Persist a tester aggregate.

        :param tester: The tester aggregate to save.
        :type tester: TesterAggregate
        :return: None
        :rtype: None
        '''

        # Reconstitute the matching config object before serializing it.
        tester_data = TesterAggregate.build_config_object(
            tester.model_dump(),
        ).to_primitive(self.default_role)

        # Store the config data in the flat tester section.
        full_data = self._load()
        full_data.setdefault('testers', {})[tester.id] = tester_data
        self._save(full_data)

    # * method: delete
    def delete(self, id: str) -> None:
        '''Delete a tester idempotently.

        :param id: The tester identifier.
        :type id: str
        :return: None
        :rtype: None
        '''

        # Remove the tester if present and persist the resulting configuration.
        full_data = self._load()
        full_data.get('testers', {}).pop(id, None)
        self._save(full_data)
