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
    An app service dependency that defines the service configuration
    for an app session.
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
        description='The unique identifier for the application session.',
    )

    # * attribute: name
    name: str = Field(
        ...,
        description='The name of the application session.',
    )

    # * attribute: description
    description: str | None = Field(
        default=None,
        description='The description of the application session.',
    )

    # * attribute: logger_id
    logger_id: str = Field(
        default='default',
        description='The logger ID for the application session.',
    )

    # * attribute: flags
    flags: List[str] = Field(
        default_factory=lambda: ['default'],
        description='The DI flags for the application session.',
    )

    # * attribute: services
    services: List[AppServiceDependency] = Field(
        default_factory=list,
        description='The application session service dependencies.',
    )

    # * attribute: constants
    constants: Dict[str, str] = Field(
        default_factory=dict,
        description='The application session dependency constants.',
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

        # Return the first matching service dependency, or None.
        return next((dep for dep in self.services if dep.service_id == service_id), None)

# ** model: app_interface
# -- obsolete: AppInterface is superseded by AppSession. Retire in Parity V Story 13.
class AppInterface(AppSession):
    '''
    Application interface definition.

    .. deprecated::
        Superseded by :class:`AppSession`. Retire in Parity V Story 13 when
        contexts and blueprints are updated to consume AppSession directly.
    '''

    # * attribute: module_path
    # -- obsolete: Context class location moved to runtime resolution. Retire in Parity V Story 13.
    module_path: str | None = Field(
        default=None,
        description='The module path for the application interface context class. Obsolete.',
    )

    # * attribute: class_name
    # -- obsolete: Context class name moved to runtime resolution. Retire in Parity V Story 13.
    class_name: str | None = Field(
        default=None,
        description='The class name for the application interface context class. Obsolete.',
    )

    # * method: apply_defaults
    # -- obsolete: Default merging moved to blueprint layer. Retire in Parity V Story 17.
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
