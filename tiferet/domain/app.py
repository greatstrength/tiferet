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

# ** model: app_session
class AppSession(DomainObject):
    '''
    The base application session object.
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


