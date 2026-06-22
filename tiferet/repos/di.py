"""Tiferet DI Configuration Repository"""

# *** imports

# ** core
from typing import Any, Dict, List, Tuple

# ** app
from ..interfaces import DIService
from ..mappers import (
    ServiceRegistrationAggregate,
    ServiceRegistrationConfigObject,
)
from .settings import ConfigurationRepository

# *** repos

# ** repo: di_yaml_repository
class DIConfigRepository(DIService, ConfigurationRepository):
    '''
    The DI YAML repository.
    '''

    # * init
    def __init__(self, di_config: str, encoding: str = 'utf-8') -> None:
        '''
        Initialize the di configuration repository.

        :param di_config: The configuration file path.
        :type di_config: str
        :param encoding: The file encoding (default is 'utf-8').
        :type encoding: str
        '''

        # Initialize the configuration repository base.
        ConfigurationRepository.__init__(self, config_file=di_config, encoding=encoding)

    # * method: registration_exists
    def registration_exists(self, id: str) -> bool:
        '''
        Check if a service registration exists by ID.

        :param id: The service registration identifier.
        :type id: str
        :return: True if the service registration exists, otherwise False.
        :rtype: bool
        '''

        # Load the services mapping from the configuration file.
        services_data = self._load(
            start_node=lambda data: data.get('services', {})
        )

        # Return whether the registration id exists in the mapping.
        return id in services_data

    # * method: get_registration
    def get_registration(self, registration_id: str, flag: str = None) -> ServiceRegistrationAggregate | None:
        '''
        Retrieve a service registration by ID, optionally filtered by flag.

        :param registration_id: The service registration identifier.
        :type registration_id: str
        :param flag: Optional flag to filter the registration.
        :type flag: str
        :return: The service registration aggregate or None if not found.
        :rtype: ServiceRegistrationAggregate | None
        '''

        # Load the specific service registration data from the configuration file.
        config_data = self._load(
            start_node=lambda data: data.get('services', {}).get(registration_id)
        )

        # If no data is found, return None.
        if not config_data:
            return None

        # Map the data to a ServiceRegistrationAggregate.
        registration = ServiceRegistrationConfigObject.model_validate(
            {**config_data, 'id': registration_id}
        ).map()

        # If a flag is provided, filter the registration by flag.
        if flag:
            dependency = registration.get_dependency(flag)
            if dependency:
                registration.module_path = dependency.module_path
                registration.class_name = dependency.class_name
                if dependency.parameters:
                    merged = dict(registration.parameters or {})
                    merged.update(dependency.parameters)
                    registration.parameters = merged

        # Return the registration.
        return registration

    # * method: list_all
    def list_all(self) -> Tuple[List[ServiceRegistrationAggregate], Dict[str, str]]:
        '''
        List all service configurations and constants.

        :return: A tuple containing a list of service registration aggregates and a dictionary of constants.
        :rtype: Tuple[List[ServiceRegistrationAggregate], Dict[str, str]]
        '''

        # Load the full configuration file.
        full_data = self._load()

        # Map each service entry to a ServiceRegistrationAggregate.
        configurations = [
            ServiceRegistrationConfigObject.model_validate(
                {**config_data, 'id': config_id}
            ).map()
            for config_id, config_data in full_data.get('services', {}).items()
        ]

        # Get the constants dictionary.
        constants = full_data.get('const', {})

        # Return the configurations and constants.
        return configurations, constants

    # * method: save_registration
    def save_registration(self, registration: ServiceRegistrationAggregate) -> None:
        '''
        Save or update a service registration.

        :param registration: The service registration aggregate to save.
        :type registration: ServiceRegistrationAggregate
        :return: None
        :rtype: None
        '''

        # Convert the service registration model to configuration data.
        config_data = ServiceRegistrationConfigObject.from_model(registration)

        # Load the full configuration file.
        full_data = self._load()

        # Update or insert the service registration entry.
        full_data.setdefault('services', {})[registration.id] = config_data.to_primitive(self.default_role)

        # Persist the updated configuration file.
        self._save(data=full_data)

    # * method: delete_registration
    def delete_registration(self, registration_id: str) -> None:
        '''
        Delete a service registration by ID. This operation is idempotent.

        :param registration_id: The service registration identifier.
        :type registration_id: str
        :return: None
        :rtype: None
        '''

        # Load the full configuration file.
        full_data = self._load()

        # Remove the service registration entry if it exists (idempotent).
        full_data.get('services', {}).pop(registration_id, None)

        # Persist the updated configuration file.
        self._save(data=full_data)

    # * method: save_constants
    def save_constants(self, constants: Dict[str, Any] = {}) -> None:
        '''
        Save or update constants.

        :param constants: The constants to save.
        :type constants: Dict[str, Any]
        :return: None
        :rtype: None
        '''

        # Load the full configuration file.
        full_data = self._load()

        # Merge existing constants with new ones.
        existing_constants = full_data.get('const', {})
        existing_constants.update(constants)

        # Remove any constants with None values.
        full_data['const'] = {k: v for k, v in existing_constants.items() if v is not None}

        # Persist the updated configuration file.
        self._save(data=full_data)
