"""Tiferet DI Domain Models"""

# *** imports

# ** core
from importlib import import_module
from typing import Dict, List

# ** infra
from pydantic import Field

# ** app
from .settings import DomainObject

# *** models

# ** model: flagged_dependency
class FlaggedDependency(DomainObject):
    '''
    A flagged container dependency object.
    '''

    # * attribute: module_path
    module_path: str = Field(
        ...,
        description='The module path.',
    )

    # * attribute: class_name
    class_name: str = Field(
        ...,
        description='The class name.',
    )

    # * attribute: flag
    flag: str = Field(
        ...,
        description='The flag for the container dependency.',
    )

    # * attribute: parameters
    parameters: Dict[str, str] = Field(
        default_factory=dict,
        description='The container dependency parameters.',
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
        description='The default configuration parameters.',
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

        Checks flagged dependencies first (in flag priority order), then
        falls back to the registration's default module_path/class_name.

        :param flags: The flags for the flagged dependency.
        :type flags: Tuple[str, ...]
        :return: The type of the service registration, or None.
        :rtype: type | None
        '''

        # Check the flagged dependencies for the type first.
        for flag in flags:
            dependency = self.get_dependency(flag)
            if dependency:
                return getattr(import_module(dependency.module_path), dependency.class_name)

        # Otherwise defer to an available default type.
        if self.module_path and self.class_name:
            return getattr(import_module(self.module_path), self.class_name)

        # Return None if no type is found.
        return None
