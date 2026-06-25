"""Tiferet App Mappers"""

# *** imports

# ** core
from typing import Any, ClassVar, Dict, List

# ** infra
from pydantic import AliasChoices, Field

# ** app
from ..domain import (
    AppServiceDependency,
    AppInterface,
)
from ..events import RaiseError, a
from .settings import (
    Aggregate,
    TransferObject,
    DEFAULT_MODULE_PATH,
    DEFAULT_CLASS_NAME,
)

# *** mappers

# ** mapper: app_interface_aggregate
class AppInterfaceAggregate(AppInterface, Aggregate):
    '''
    An aggregate representation of an app interface contract.
    '''

    # * method: add_service
    def add_service(
        self,
        module_path: str,
        class_name: str,
        service_id: str,
        parameters: Dict[str, str] | None = None,
    ) -> None:
        '''
        Add a service dependency to the app interface.

        :param module_path: The module path for the service dependency.
        :type module_path: str
        :param class_name: The class name for the service dependency.
        :type class_name: str
        :param service_id: The id for the service dependency.
        :type service_id: str
        :param parameters: Additional parameters for the service dependency.
        :type parameters: Dict[str, str] | None
        :return: None
        :rtype: None
        '''

        # Create a new AppServiceDependency object.
        dependency = AppServiceDependency(
            module_path=module_path,
            class_name=class_name,
            service_id=service_id,
            parameters=parameters or {},
        )

        # Add the service dependency via list reassignment.
        self.services = list(self.services) + [dependency]

    # * method: remove_service
    # + todo: remove attribute_id parameter once the dependency with the app event tests has been resolved
    def remove_service(
        self,
        service_id: str | None = None,
        attribute_id: str | None = None,
    ) -> AppServiceDependency | None:
        '''
        Remove and return a service dependency by its service_id (idempotent).

        If a service dependency with the given service_id exists, it is removed.
        If no matching service dependency exists, no action is taken (silent success).

        :param service_id: The service_id of the service dependency to remove.
        :type service_id: str | None
        :param attribute_id: Deprecated alias for service_id.
        :type attribute_id: str | None
        :return: The removed AppServiceDependency or None.
        :rtype: AppServiceDependency | None
        '''

        # Fall back to attribute_id if service_id is not provided.
        if service_id is None and attribute_id is not None:
            service_id = attribute_id

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
    # + todo: remove attribute_id parameter once the dependency with the app event tests has been resolved
    def set_service(
        self,
        service_id: str | None = None,
        module_path: str | None = None,
        class_name: str | None = None,
        parameters: Dict[str, Any] | None = None,
        attribute_id: str | None = None,
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
        :type service_id: str | None
        :param module_path: The module path.
        :type module_path: str | None
        :param class_name: The class name.
        :type class_name: str | None
        :param parameters: New parameters (None to clear).
        :type parameters: Dict[str, Any] | None
        :param attribute_id: Deprecated alias for service_id.
        :type attribute_id: str | None
        :return: None
        :rtype: None
        '''

        # Fall back to attribute_id if service_id is not provided.
        if service_id is None and attribute_id is not None:
            service_id = attribute_id

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

    # * method: set_attribute
    def set_attribute(self, attribute: str, value: Any) -> None:
        '''
        Update a supported scalar attribute on the app interface aggregate.

        Supported attributes: name, description, module_path, class_name,
        logger_id, flags.

        :param attribute: The attribute name to update.
        :type attribute: str
        :param value: The new value.
        :type value: Any
        :return: None
        :rtype: None
        '''

        # Define the set of supported attributes.
        supported = {
            'name',
            'description',
            'module_path',
            'class_name',
            'logger_id',
            'flags',
        }

        # Validate the attribute name.
        if attribute not in supported:
            RaiseError.execute(
                error_code=a.const.INVALID_MODEL_ATTRIBUTE_ID,
                message='Invalid attribute: {attribute}. Supported attributes are {supported}.',
                attribute=attribute,
                supported=', '.join(sorted(supported)),
            )

        # Specific validation for module_path and class_name.
        if attribute in {'module_path', 'class_name'}:
            if not value or not str(value).strip():
                RaiseError.execute(
                    error_code=a.const.INVALID_APP_INTERFACE_TYPE_ID,
                    message='{attribute} must be a non-empty string.',
                    attribute=attribute,
                )

        # Apply the update; validate_assignment=True handles re-validation.
        setattr(self, attribute, value)


# ** mapper: app_service_dependency_config_object
class AppServiceDependencyConfigObject(AppServiceDependency, TransferObject):
    '''
    A configuration data representation of an app service dependency object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'parameters', 'service_id'}},
        'to_data.yaml': {'by_alias': True, 'exclude': {'service_id'}},
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


# ** mapper: app_interface_config_object
class AppInterfaceConfigObject(AppInterface, TransferObject):
    '''
    A configuration data representation of an app interface settings object.
    '''

    # * attribute: _ROLES
    _ROLES: ClassVar[Dict[str, Dict[str, Any]]] = {
        'to_model': {'exclude': {'services', 'constants', 'module_path', 'class_name'}},
        'to_data.yaml': {'by_alias': True, 'exclude': {'id'}},
    }

    # * attribute: module_path
    module_path: str = Field(
        default=DEFAULT_MODULE_PATH,
        serialization_alias='module',
        validation_alias=AliasChoices('module_path', 'module'),
        description='The app context module path for the app settings.',
    )

    # * attribute: class_name
    class_name: str = Field(
        default=DEFAULT_CLASS_NAME,
        serialization_alias='class',
        validation_alias=AliasChoices('class_name', 'class'),
        description='The class name for the app context.',
    )

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
    def map(self, **overrides) -> AppInterfaceAggregate:
        '''
        Maps the app interface data to an app interface aggregate.

        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new app interface aggregate.
        :rtype: AppInterfaceAggregate
        '''

        # Map the app interface data with dict→list conversion for services.
        return super().map(
            AppInterfaceAggregate,
            module_path=self.module_path,
            class_name=self.class_name,
            services=[dep.map(service_id=dep_id) for dep_id, dep in (self.services or {}).items()],
            constants=dict(self.constants or {}),
            **overrides,
        )

    # * method: from_model
    @classmethod
    def from_model(cls, app_interface: AppInterface, **overrides) -> 'AppInterfaceConfigObject':
        '''
        Creates an AppInterfaceConfigObject from an AppInterface model.

        :param app_interface: The app interface model.
        :type app_interface: AppInterface
        :param overrides: Additional keyword arguments.
        :type overrides: dict
        :return: A new AppInterfaceConfigObject.
        :rtype: AppInterfaceConfigObject
        '''

        # Create a new AppInterfaceConfigObject from the model, converting
        # the services list into a dictionary keyed by service_id.
        return super().from_model(
            app_interface,
            services={
                dep.service_id: AppServiceDependencyConfigObject.from_model(dep)
                for dep in app_interface.services
            },
            **overrides,
        )
