"""Tiferet App Domain Models"""

# *** imports

# ** core
from importlib import import_module
from typing import Dict, List

# ** infra
from pydantic import Field

# ** app
from ..di import ServiceProvider
from .settings import DomainObject

# *** models

# ** model: app_service_dependency
class AppServiceDependency(DomainObject):
    '''
    An app service dependency that defines the service configuration for an app interface.
    '''

    # * attribute: service_id
    service_id: str = Field(
        ...,
        description='The service id for the application dependency.',
    )

    # * attribute: module_path
    module_path: str = Field(
        ...,
        description='The module path for the app dependency.',
    )

    # * attribute: class_name
    class_name: str = Field(
        ...,
        description='The class name for the app dependency.',
    )

    # * attribute: parameters
    parameters: Dict[str, str] = Field(
        default_factory=dict,
        description='The parameters for the application dependency.',
    )

    # * method: get_service_type
    def get_service_type(self) -> type:
        '''
        Get the service type for this app service dependency.

        :return: The service type.
        :rtype: type
        '''

        # Import and return the service class type.
        return getattr(import_module(self.module_path), self.class_name)

# ** model: app_interface
class AppInterface(DomainObject):
    '''
    The base application interface object.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='The unique identifier for the application interface.',
    )

    # * attribute: name
    name: str = Field(
        ...,
        description='The name of the application interface.',
    )

    # * attribute: description
    description: str | None = Field(
        default=None,
        description='The description of the application interface.',
    )

    # * attribute: module_path
    module_path: str = Field(
        ...,
        description='The module path for the application instance context.',
    )

    # * attribute: class_name
    class_name: str = Field(
        ...,
        description='The class name for the application instance context.',
    )

    # * attribute: service_provider_path
    service_provider_path: str = Field(
        default='tiferet.di.dynamic',
        description='The module path for the service provider to use for this dependency.',
    )

    # * attribute: service_provider_class_name
    service_provider_class_name: str = Field(
        default='DynamicServiceProvider',
        description='The class name for the service provider to use for this dependency.',
    )

    # * attribute: logger_id
    logger_id: str = Field(
        default='default',
        description='The logger ID for the application instance.',
    )

    # * attribute: flags
    flags: List[str] = Field(
        default_factory=lambda: ['default'],
        description='The flags for the application interface.',
    )

    # * attribute: services
    services: List[AppServiceDependency] = Field(
        default_factory=list,
        description='The application instance service dependencies.',
    )

    # * attribute: constants
    constants: Dict[str, str] = Field(
        default_factory=dict,
        description='The application dependency constants.',
    )

    # * method: get_service
    def get_service(self, service_id: str) -> AppServiceDependency | None:
        '''
        Get the service dependency by service id.

        :param service_id: The service id of the service dependency.
        :type service_id: str
        :return: The matching service dependency, or ``None``.
        :rtype: AppServiceDependency | None
        '''

        # Get the service dependency by service id.
        return next((dep for dep in self.services if dep.service_id == service_id), None)

    # * method: get_service_type_mapping
    def get_service_type_mapping(self) -> Dict[str, type]:
        '''
        Get a mapping of service IDs to their corresponding types.

        :return: A dictionary mapping service IDs to their types.
        :rtype: Dict[str, type]
        '''

        # Register scalars and constants first.
        dependencies: Dict[str, type] = dict(
            interface_id=self.id,
            logger_id=getattr(self, 'logger_id', None),
        )

        # Add the constants from the app interface to the dependencies.
        dependencies.update(self.constants)

        # Add the remaining app context service dependencies and parameters.
        for dep in self.services:
            dependencies[dep.service_id] = dep.get_service_type()
            for param, value in dep.parameters.items():
                dependencies[param] = value

        # Return the assembled dependencies mapping. The application interface
        # context itself is constructed declaratively by the blueprint, so it is
        # intentionally not registered here as a DI-resolved service.
        return dependencies

    # * method: create_service_provider
    def create_service_provider(self) -> ServiceProvider:
        '''
        Create a service provider for this app interface.

        :return: A configured service provider instance.
        :rtype: ServiceProvider
        '''

        # Build the service type mapping for this interface.
        type_map = self.get_service_type_mapping()

        # Resolve the configured service provider class.
        provider_class = getattr(
            import_module(self.service_provider_path),
            self.service_provider_class_name,
        )

        # Create and return the configured service provider instance.
        return provider_class(services=type_map)
