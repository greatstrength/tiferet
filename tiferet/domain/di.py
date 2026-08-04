"""Tiferet DI Domain Models"""

# *** imports

# ** core
from typing import Dict, List

# ** infra
from pydantic import Field

# ** app
from .core import DomainObject, ServiceDependency

# *** models

# ** model: flagged_dependency
class FlaggedDependency(ServiceDependency):
    '''
    A flagged container dependency object.
    '''

    # * attribute: flag
    flag: str = Field(
        ...,
        description='The flag for the container dependency.',
    )

# ** model: service_registration
class ServiceRegistration(DomainObject):
    '''
    A service registration that defines dependency injection behavior.
    '''

    # * attribute: id
    id: str = Field(
        ...,
        description='The unique identifier for the service registration.',
    )

    # * attribute: name
    name: str | None = Field(
        default=None,
        description='The name of the service registration.',
    )

    # * attribute: module_path
    module_path: str | None = Field(
        default=None,
        description='The default module path for the dependency class.',
    )

    # * attribute: class_name
    class_name: str | None = Field(
        default=None,
        description='The default class name for the dependency class.',
    )

    # * attribute: parameters
    parameters: Dict[str, str] = Field(
        default_factory=dict,
        description='The default registration parameters.',
    )

    # * attribute: dependencies
    dependencies: List[FlaggedDependency] = Field(
        default_factory=list,
        description='The flag-specific implementation overrides.',
    )

    # * method: get_dependency
    def get_dependency(self, *flags) -> FlaggedDependency | None:
        '''
        Gets a flagged dependency by flag.

        :param flags: The flags to match against flagged dependencies.
        :type flags: Tuple[str, ...]
        :return: The first flagged dependency matching any provided flag, or None.
        :rtype: FlaggedDependency | None
        '''

        # Return the first dependency that matches any of the provided flags.
        # Input flags are assumed ordinal in priority, so the first match is returned.
        for flag in flags:
            match = next(
                (dependency for dependency in self.dependencies if dependency.flag == flag),
                None,
            )
            if match:
                return match

        # Return None if no dependency matches the flags.
        return None

    # * method: get_service_type
    def get_service_type(self, *flags) -> type | None:
        '''
        Gets the service type based on the provided flags.

        Delegates to :meth:`resolve_service` so the flagged-override
        → default precedence lives in exactly one place, then imports
        the effective service type.

        :param flags: The flags for the flagged dependency.
        :type flags: Tuple[str, ...]
        :return: The type of the service registration, or None.
        :rtype: type | None
        '''

        # Resolve the effective dependency for these flags, then import its type.
        dependency = self.resolve_service(*flags)
        return dependency.get_service_type() if dependency else None

    # * method: resolve_service
    def resolve_service(self, *flags) -> ServiceDependency | None:
        '''
        Resolve the effective core service dependency for the given flags.

        Prefers a matching flagged override (in flag priority order), then
        falls back to the registration's own default definition, and returns
        ``None`` when no service is defined.

        :param flags: The flags to match against flagged dependencies.
        :type flags: Tuple[str, ...]
        :return: The effective core service dependency, or None.
        :rtype: ServiceDependency | None
        '''

        # Prefer a flagged override when one matches (flag priority order).
        dependency = self.get_dependency(*flags)
        if dependency:
            return ServiceDependency(
                module_path=dependency.module_path,
                class_name=dependency.class_name,
                parameters=dependency.parameters,
            )

        # Fall back to the registration's default definition when fully specified.
        if self.module_path and self.class_name:
            return ServiceDependency(
                module_path=self.module_path,
                class_name=self.class_name,
                parameters=self.parameters,
            )

        # Return None when no service is defined for these flags.
        return None
