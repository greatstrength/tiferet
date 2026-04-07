"""Tiferet App Domain Models"""

# *** imports

# ** core
from importlib import import_module
from typing import Dict

from tiferet.events.static import ImportDependency

# ** app
from ..di import ServiceProvider
from .settings import (
    DomainObject,
    StringType,
    ListType,
    DictType,
    ModelType,
)

# *** models

# ** model: app_service_dependency
class AppServiceDependency(DomainObject):
    '''
    An app service dependency that defines the service configuration for an app interface.
    '''

    # * attribute: service_id
    service_id = StringType(
        required=True,
        metadata=dict(
            description='The service id for the application dependency.'
        ),
    )

    # * attribute: module_path
    module_path = StringType(
        required=True,
        metadata=dict(
            description='The module path for the app dependency.'
        ),
    )

    # * attribute: class_name
    class_name = StringType(
        required=True,
        metadata=dict(
            description='The class name for the app dependency.'
        ),
    )

    # * attribute: parameters
    parameters = DictType(
        StringType,
        default={},
        metadata=dict(
            description='The parameters for the application dependency.'
        ),
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
    id = StringType(
        required=True,
        metadata=dict(
            description='The unique identifier for the application interface.'
        ),
    )

    # * attribute: name
    name = StringType(
        required=True,
        metadata=dict(
            description='The name of the application interface.'
        ),
    )

    # * attribute: description
    description = StringType(
        metadata=dict(
            description='The description of the application interface.'
        ),
    )

    # * attribute: module_path
    module_path = StringType(
        required=True,
        metadata=dict(
            description='The module path for the application instance context.'
        ),
    )

    # * attribute: class_name
    class_name = StringType(
        required=True,
        metadata=dict(
            description='The class name for the application instance context.'
        ),
    )

    # * attribute: service_provider_path
    service_provider_path = StringType(
        default='tiferet.di.dependencies',
        metadata=dict(
            description='The module path for the service provider to use for this dependency.'
        ),
    )

    # * attribute: service_provider_class_name
    service_provider_class_name = StringType(
        default='DependenciesServiceProvider',
        metadata=dict(
            description='The class name for the service provider to use for this dependency.'
        ),
    )

    # * attribute: logger_id
    logger_id = StringType(
        default='default',
        metadata=dict(
            description='The logger ID for the application instance.'
        ),
    )

    # * attribute: flags
    flags = ListType(
        StringType(),
        default=['default'],
        metadata=dict(
            description='The flags for the application interface.'
        ),
    )

    # * attribute: services
    services = ListType(
        ModelType(AppServiceDependency),
        required=True,
        default=[],
        metadata=dict(
            description='The application instance service dependencies.'
        ),
    )

    # * attribute: constants
    constants = DictType(
        StringType,
        default={},
        metadata=dict(
            description='The application dependency constants.'
        ),
    )

    # * method: get_service
    def get_service(self, service_id: str) -> AppServiceDependency:
        '''
        Get the service dependency by service id.

        :param service_id: The service id of the service dependency.
        :type service_id: str
        :return: The service dependency.
        :rtype: AppServiceDependency
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

        # Retrieve the app context dependency, interface id, and logger id.
        dependencies = dict(
            app_context=getattr(import_module(self.module_path),
                self.class_name,
            ),
            interface_id=self.id,
            logger_id=getattr(self, 'logger_id', None),
        )
        
        # Add the constants from the app interface to the dependencies.
        dependencies.update(self.constants)

        # Add the remaining app context service dependencies and parameters.
        # Service-specific parameters may override constants if needed.
        for dep in self.services:
            dependencies[dep.service_id] = dep.get_service_type()
            for param, value in dep.parameters.items():
                dependencies[param] = value

        # Return the assembled dependencies mapping.
        return dependencies
    
    # * method: create_service_provider
    def create_service_provider(self) -> ServiceProvider:
        '''
        Create a service provider instance for this app interface.

        :return: A configured service provider instance for this app interface.
        :rtype: ServiceProvider
        '''

        # Get the service type mapping from the app interface.
        type_map = self.get_service_type_mapping()

        # Create and return the service provider instance using the specified provider class.
        provider_class = getattr(import_module(self.service_provider_path),
            self.service_provider_class_name,
        )
        return provider_class(services=type_map)
