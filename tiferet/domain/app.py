"""Tiferet App Domain Models"""

# *** imports

# ** core
from typing import Dict, List

# ** infra
from pydantic import Field

# ** app
from .core import DomainObject, ServiceDependency

# *** models

# ** model: app_service_dependency
class AppServiceDependency(ServiceDependency):
    '''
    An app service dependency that defines the service configuration for an app interface.
    '''

    # * attribute: service_id
    service_id: str = Field(
        ...,
        description='The service id for the application dependency.',
    )

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

    # * method: apply_defaults
    def apply_defaults(self,
            default_services: List[AppServiceDependency] = None,
            default_constants: Dict[str, str] = None,
        ) -> 'AppInterface':
        '''
        Return a new app interface with framework default services and constants applied.

        Default services are added for any ``service_id`` not already present, and
        default constants are added only for keys the interface does not already
        define (existing values win). This is a non-mutating derivation: the
        current interface is left unchanged and a new instance is returned.

        :param default_services: Default service dependencies to merge.
        :type default_services: List[AppServiceDependency] | None
        :param default_constants: Default constants to merge for missing keys.
        :type default_constants: Dict[str, str] | None
        :return: A new app interface with the defaults applied.
        :rtype: AppInterface
        '''

        # Append any default service whose service_id is not already present.
        services = list(self.services)
        existing_ids = {dep.service_id for dep in services}
        for dep in (default_services or []):
            if dep.service_id not in existing_ids:
                services.append(dep)
                existing_ids.add(dep.service_id)

        # Merge default constants only for keys not already defined (existing win).
        constants = {**(default_constants or {}), **(self.constants or {})}

        # Return a new interface with the merged services and constants.
        return self.model_copy(update=dict(services=services, constants=constants))
