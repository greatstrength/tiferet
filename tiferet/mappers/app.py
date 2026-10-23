"""Tiferet App Mappers"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict, List

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
    An aggregate representation of an app session.
    '''

    # * attribute: _SETTABLE_ATTRIBUTES
    _SETTABLE_ATTRIBUTES: ClassVar[set] = {'name', 'description', 'logger_id', 'flags'}

    # * method: add_service
    def add_service(
        self,
        service_id: str,
        module_path: str,
        class_name: str,
        parameters: Dict[str, str] | None = None,
    ) -> None:
        '''
        Add a service dependency to the app session. The service_id must be
        absent; adding a present service_id raises a model error and leaves
        the list unchanged. ``None`` values in ``parameters`` are not stored.

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

        # Refuse a service_id that is already present.
        if self.get_service(service_id) is not None:
            ModelError.raise_error(
                INVALID_MODEL_VALUE_ID,
                message=f'Service dependency {service_id!r} already exists in app session {self.id!r}.',
            )

        # Create a new AppServiceDependency object without None-valued parameters.
        dependency = AppServiceDependency(
            service_id=service_id,
            module_path=module_path,
            class_name=class_name,
            parameters={k: v for k, v in (parameters or {}).items() if v is not None},
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
        Every entry with that service_id is dropped; the first is returned.

        :param service_id: The service_id of the service dependency to remove.
        :type service_id: str
        :return: The removed AppServiceDependency or None.
        :rtype: AppServiceDependency | None
        '''

        # Return None when no match was found (idempotent).
        removed = self.get_service(service_id)
        if removed is None:
            return None

        # Drop every entry with that service_id and return the first.
        self.services = [
            dep for dep in self.services
            if dep.service_id != service_id
        ]
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

        An existing service_id is updated in place; an absent one is appended.
        On an update, ``parameters`` is an overlay: A new value wins, a ``None`` value removes that key, and a ``None`` argument leaves the mapping unchanged.
        On create, a ``None`` argument stores ``{}`` and ``None`` values are
        not stored.

        :param service_id: The service dependency identifier.
        :type service_id: str
        :param module_path: The module path.
        :type module_path: str | None
        :param class_name: The class name.
        :type class_name: str | None
        :param parameters: The parameter overlay (None leaves the parameters).
        :type parameters: Dict[str, Any] | None
        :return: None
        :rtype: None
        '''

        # Find the existing dependency by service_id.
        dep = self.get_service(service_id)

        # Update in place when an existing dependency is found.
        if dep is not None:
            dep.module_path = module_path
            dep.class_name = class_name

            # Merge and remove None-valued keys; a None argument leaves the parameters.
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

        # If the service dependency does not exist, create a new one and reassign.
        new_dep = AppServiceDependency(
            service_id=service_id,
            module_path=module_path,
            class_name=class_name,
            parameters={k: v for k, v in (parameters or {}).items() if v is not None},
        )
        self.services = list(self.services) + [new_dep]

    # * method: set_constants
    def set_constants(self, constants: Dict[str, Any] | None = None) -> None:
        '''
        Update the constants dictionary.

        :param constants: New constants to merge, or None to clear all.
            Keys with ``None`` values are removed.
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
        Map the app service dependency data to a runtime AppServiceDependency.

        :param service_id: The id to assign to the dependency.
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
    A configuration data representation of an app session settings object.
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
        description='The app instance service dependencies.',
    )

    # * attribute: constants
    constants: Dict[str, str] = Field(
        default_factory=dict,
        serialization_alias='const',
        validation_alias=AliasChoices('constants', 'const'),
        description='The constants for the app settings.',
    )

    # * method: map
    def map(self, **overrides) -> AppSessionAggregate:
        '''
        Map the app session data to an app session aggregate.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new app session aggregate.
        :rtype: AppSessionAggregate
        '''

        # Map the app session data with dict→list conversion for services.
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
        Creates an AppSessionConfigObject from an AppSession model.

        :param app_session: The app session model.
        :type app_session: AppSession
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new AppSessionConfigObject.
        :rtype: AppSessionConfigObject
        '''

        # Refuse a repeated service_id rather than collapsing it.
        seen = set()
        for dep in app_session.services:
            if dep.service_id in seen:
                ModelError.raise_error(
                    INVALID_MODEL_VALUE_ID,
                    message=f'Service dependency {dep.service_id!r} is repeated in app session {app_session.id!r}.',
                )
            seen.add(dep.service_id)

        # Create a new AppSessionConfigObject from the model, converting
        # the services list into a dictionary keyed by service_id.
        return super().from_model(
            app_session,
            services={
                dep.service_id: AppServiceDependencyConfigObject.from_model(dep)
                for dep in app_session.services
            },
            **overrides,
        )

