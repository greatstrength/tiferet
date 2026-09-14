"""Tiferet App Mappers"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict, List

# ** infra
from pydantic import AliasChoices, Field

# ** app
from ..domain import (
    AppServiceDependency,
    AppSession,
)
from .core import (
    Aggregate,
    TransferObject,
)

# *** mappers

# ** mapper: app_session_aggregate
class AppSessionAggregate(AppSession, Aggregate):
    '''
    Mutable aggregate for the AppSession domain object.
    '''

    # * attribute: _SETTABLE_ATTRIBUTES
    _SETTABLE_ATTRIBUTES: ClassVar[set] = {
        'name',
        'description',
        'logger_id',
        'flags',
    }

    # * method: add_service
    def add_service(
        self,
        service_id: str,
        module_path: str,
        class_name: str,
        parameters: Dict[str, str] | None = None,
    ) -> None:
        '''
        Add a service dependency to the app session.

        :param service_id: The id for the service dependency.
        :type service_id: str
        :param module_path: The module path for the service dependency.
        :type module_path: str
        :param class_name: The class name for the service dependency.
        :type class_name: str
        :param parameters: Additional parameters for the service dependency.
        :type parameters: Dict[str, str] | None
        :return: None
        :rtype: None
        '''

        # Create a new AppServiceDependency object.
        dependency = AppServiceDependency(
            service_id=service_id,
            module_path=module_path,
            class_name=class_name,
            parameters=parameters or {},
        )

        # Add the service dependency via list reassignment.
        self.services = list(self.services) + [dependency]

    # * method: remove_service
    def remove_service(
        self,
        service_id: str,
    ) -> AppServiceDependency | None:
        '''
        Remove and return a service dependency by its service_id (idempotent).

        If a service dependency with the given service_id exists, it is removed.
        If no matching service dependency exists, no action is taken (silent success).

        :param service_id: The service_id of the service dependency to remove.
        :type service_id: str
        :return: The removed AppServiceDependency or None.
        :rtype: AppServiceDependency | None
        '''

        # Work on a local copy; reassign only when a match is found.
        services = list(self.services)
        for index, dep in enumerate(services):
            if dep.service_id == service_id:
                removed = services.pop(index)
                self.services = services
                return removed

        # If no service dependency matches, return None without modifying the list.
        return None

    # * method: set_service
    def set_service(
        self,
        service_id: str,
        module_path: str | None = None,
        class_name: str | None = None,
        parameters: Dict[str, Any] | None = None,
    ) -> None:
        '''
        Set or update a service dependency by service_id (PUT semantics).

        If a service dependency with the given service_id exists:
          - Update module_path and class_name.
          - Merge parameters (favor new values; remove keys with None value).
          - Clear parameters if parameters is None.

        If no service dependency exists:
          - Create new AppServiceDependency and append to services.

        :param service_id: The service dependency identifier.
        :type service_id: str
        :param module_path: The module path.
        :type module_path: str | None
        :param class_name: The class name.
        :type class_name: str | None
        :param parameters: New parameters (None to clear).
        :type parameters: Dict[str, Any] | None
        :return: None
        :rtype: None
        '''

        # Find the existing service dependency by service_id.
        dep = self.get_service(service_id)

        # If the service dependency exists, update its type fields and merge parameters.
        if dep is not None:
            dep.module_path = module_path
            dep.class_name = class_name

            # Clear parameters when parameters is None.
            if parameters is None:
                dep.parameters = {}

            # Otherwise merge and then remove keys whose value is None.
            else:
                merged = dict(dep.parameters or {})
                merged.update(parameters)
                dep.parameters = {
                    key: value
                    for key, value in merged.items()
                    if value is not None
                }

            # Return early after in-place update.
            return

        # If the service dependency does not exist, create a new one and reassign.
        new_dep = AppServiceDependency(
            service_id=service_id,
            module_path=module_path,
            class_name=class_name,
            parameters=parameters or {},
        )
        self.services = list(self.services) + [new_dep]

    # * method: set_constants
    def set_constants(self, constants: Dict[str, Any] | None = None) -> None:
        '''
        Update the constants dictionary.

        :param constants: New constants to merge, or None to clear all. Keys with None value are removed.
        :type constants: Dict[str, Any] | None
        :return: None
        :rtype: None
        '''

        # Clear all constants when None is provided.
        if constants is None:
            self.constants = {}
            return

        # Merge new constants and remove keys with None value.
        merged = dict(self.constants or {})
        merged.update(constants)
        self.constants = {
            key: value
            for key, value in merged.items()
            if value is not None
        }


# ** mapper: app_service_dependency_config_object
class AppServiceDependencyConfigObject(AppServiceDependency, TransferObject):
    '''
    A configuration data representation of an app service dependency object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'parameters', 'service_id'}},
        'to_data': {'by_alias': True, 'exclude': {'service_id'}},
    }

    # * attribute: service_id
    service_id: str | None = Field(
        default=None,
        description='The service id for the application dependency that is not required for assembly.',
    )

    # * attribute: parameters
    parameters: Dict[str, str] = Field(
        default_factory=dict,
        serialization_alias='params',
        validation_alias=AliasChoices('params', 'parameters'),
        description='The parameters for the application dependency that are not required for assembly.',
    )

    # * method: map
    def map(self, service_id: str, **overrides) -> AppServiceDependency:
        '''
        Maps the app service dependency data to an app service dependency object.

        :param service_id: The id for the app service dependency.
        :type service_id: str
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new app service dependency object.
        :rtype: AppServiceDependency
        '''

        # Map to the app service dependency object, injecting service_id and parameters.
        return super().map(
            AppServiceDependency,
            service_id=service_id,
            parameters=dict(self.parameters or {}),
            **overrides,
        )

    # * method: from_model
    @classmethod
    def from_model(cls, dependency: AppServiceDependency, **overrides) -> 'AppServiceDependencyConfigObject':
        '''
        Creates an AppServiceDependencyConfigObject from an AppServiceDependency model.

        :param dependency: The app service dependency model.
        :type dependency: AppServiceDependency
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new AppServiceDependencyConfigObject.
        :rtype: AppServiceDependencyConfigObject
        '''

        # Create a new AppServiceDependencyConfigObject from the model.
        return super().from_model(dependency, **overrides)


# ** mapper: app_session_config_object
class AppSessionConfigObject(AppSession, TransferObject):
    '''
    Configuration data representation of the AppSession domain object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'services', 'constants'}},
        'to_data': {'by_alias': True, 'exclude': {'id'}},
    }

    # * attribute: services
    services: Dict[str, AppServiceDependencyConfigObject] = Field(
        default_factory=dict,
        serialization_alias='attrs',
        validation_alias=AliasChoices('attrs', 'services', 'dependencies', 'attributes'),
        description='The application session service dependencies, keyed by service_id.',
    )

    # * attribute: constants
    constants: Dict[str, str] = Field(
        default_factory=dict,
        serialization_alias='const',
        validation_alias=AliasChoices('constants', 'const'),
        description='The application session dependency constants.',
    )

    # * method: map
    def map(self, **overrides) -> AppSessionAggregate:
        '''
        Map the app session configuration data to an AppSessionAggregate.

        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The mapped AppSessionAggregate.
        :rtype: AppSessionAggregate
        '''

        # Map the services dict to a list and delegate to the base map.
        return super().map(
            AppSessionAggregate,
            services=[dep.map(service_id=dep_id) for dep_id, dep in (self.services or {}).items()],
            constants=dict(self.constants or {}),
            **overrides,
        )

    # * method: from_model
    @classmethod
    def from_model(cls, app_session: AppSession, **overrides) -> 'AppSessionConfigObject':
        '''
        Create an AppSessionConfigObject from an AppSession model.

        :param app_session: The AppSession domain object.
        :type app_session: AppSession
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The constructed AppSessionConfigObject.
        :rtype: AppSessionConfigObject
        '''

        # Convert the services list to a dict keyed by service_id.
        return super().from_model(
            app_session,
            services={
                dep.service_id: AppServiceDependencyConfigObject.from_model(dep)
                for dep in app_session.services
            },
            **overrides,
        )
