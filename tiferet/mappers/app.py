"""Tiferet App Mappers"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict

# ** infra
from pydantic import AliasChoices, Field

# ** app
from ..domain import (
    INVALID_MODEL_VALUE_ID,
    AppServiceDependency,
    AppSession,
    ModelError,
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
        Add a new service dependency to the app session.

        An existing service_id is rejected before the services list is changed.
        The new dependency omits parameters whose value is None, and a None
        argument creates an empty parameters mapping.

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

        # Reject an existing service_id before mutating the services list.
        if self.get_service(service_id) is not None:
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message=f'Service dependency {service_id!r} already exists in app session {self.id!r}.',
                model=self,
                attribute='services',
                service_id=service_id,
            )

        # Create a new AppServiceDependency object, omitting None-valued parameters.
        dependency = AppServiceDependency(
            service_id=service_id,
            module_path=module_path,
            class_name=class_name,
            parameters={
                key: value
                for key, value in (parameters or {}).items()
                if value is not None
            },
        )

        # Add the service dependency via list reassignment.
        self.services = list(self.services) + [dependency]

    # * method: remove_service
    def remove_service(
        self,
        service_id: str,
    ) -> AppServiceDependency | None:
        '''
        Remove every service dependency with the given service_id (idempotent).

        When a match exists, every entry with that service_id is removed, the
        surviving entries keep their order, and the first match is returned.
        When no entry matches, the services list is left as is and None is returned.

        :param service_id: The service_id of the service dependency to remove.
        :type service_id: str
        :return: The first removed AppServiceDependency or None.
        :rtype: AppServiceDependency | None
        '''

        # Find the first matching service dependency.
        removed = self.get_service(service_id)

        # If no service dependency matches, return None without modifying the list.
        if removed is None:
            return None

        # Remove every matching entry via list reassignment, preserving survivor order.
        self.services = [
            dep
            for dep in self.services
            if dep.service_id != service_id
        ]

        # Return the first matched service dependency.
        return removed

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

        If a service dependency with the given service_id exists, its first match
        is updated in place without moving it:
          - Assign module_path and class_name, even when None.
          - Overlay parameters: a new value wins and a None value removes that key.
          - A None argument leaves the existing parameters unchanged.

        If no service dependency exists:
          - Append a new AppServiceDependency whose parameters omit None values;
            a None argument creates an empty parameters mapping.

        :param service_id: The service dependency identifier.
        :type service_id: str
        :param module_path: The module path.
        :type module_path: str | None
        :param class_name: The class name.
        :type class_name: str | None
        :param parameters: The parameter overlay, or None to leave existing parameters unchanged.
        :type parameters: Dict[str, Any] | None
        :return: None
        :rtype: None
        '''

        # Find the existing service dependency by service_id.
        dep = self.get_service(service_id)

        # If the service dependency exists, update its type fields in place.
        if dep is not None:
            dep.module_path = module_path
            dep.class_name = class_name

            # Overlay parameters unless None, then remove keys whose value is None.
            if parameters is not None:
                merged = dict(dep.parameters or {})
                merged.update(parameters)
                dep.parameters = {
                    key: value
                    for key, value in merged.items()
                    if value is not None
                }

            # Return early after in-place update.
            return

        # Otherwise append a new service dependency, omitting None-valued parameters.
        new_dep = AppServiceDependency(
            service_id=service_id,
            module_path=module_path,
            class_name=class_name,
            parameters={
                key: value
                for key, value in (parameters or {}).items()
                if value is not None
            },
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

        The services list is keyed by service_id in list order. A repeated
        service_id is rejected before conversion, and the model is not mutated.

        :param app_session: The AppSession domain object.
        :type app_session: AppSession
        :param overrides: Additional field overrides.
        :type overrides: dict
        :return: The constructed AppSessionConfigObject.
        :rtype: AppSessionConfigObject
        '''

        # Reject the first repeated service_id before keyed conversion.
        seen = set()
        for dep in app_session.services:
            if dep.service_id in seen:
                ModelError.raise_error(
                    INVALID_MODEL_VALUE_ID,
                    message=f'Service dependency {dep.service_id!r} is repeated in app session {app_session.id!r}.',
                    model=app_session,
                    attribute='services',
                    service_id=dep.service_id,
                )
            seen.add(dep.service_id)

        # Convert the services list to a dict keyed by service_id.
        return super().from_model(
            app_session,
            services={
                dep.service_id: AppServiceDependencyConfigObject.from_model(dep)
                for dep in app_session.services
            },
            **overrides,
        )
