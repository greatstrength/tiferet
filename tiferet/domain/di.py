"""Tiferet DI Domain Models"""

# *** imports

# ** app
from .settings import (
    DomainObject,
    StringType,
    ListType,
    DictType,
    ModelType,
)

# *** models

# ** model: flagged_dependency
class FlaggedDependency(DomainObject):
    '''
    A flagged container dependency object.
    '''

    # * attribute: module_path
    module_path = StringType(
        required=True,
        metadata=dict(
            description='The module path.'
        ),
    )

    # * attribute: class_name
    class_name = StringType(
        required=True,
        metadata=dict(
            description='The class name.'
        ),
    )

    # * attribute: flag
    flag = StringType(
        required=True,
        metadata=dict(
            description='The flag for the container dependency.'
        ),
    )

    # * attribute: parameters
    parameters = DictType(
        StringType,
        default={},
        metadata=dict(
            description='The container dependency parameters.'
        ),
    )


# ** model: service_configuration
class ServiceConfiguration(DomainObject):
    '''
    A service configuration that defines dependency injection behavior.
    '''

    # * attribute: id
    id = StringType(
        required=True,
        metadata=dict(
            description='The unique identifier for the service configuration.'
        ),
    )

    # * attribute: name
    name = StringType(
        metadata=dict(
            description='The name of the service configuration.'
        ),
    )

    # * attribute: module_path
    module_path = StringType(
        metadata=dict(
            description='The default module path for the dependency class.'
        ),
    )

    # * attribute: class_name
    class_name = StringType(
        metadata=dict(
            description='The default class name for the dependency class.'
        ),
    )

    # * attribute: parameters
    parameters = DictType(
        StringType,
        default={},
        metadata=dict(
            description='The default configuration parameters.'
        ),
    )

    # * attribute: dependencies
    dependencies = ListType(
        ModelType(FlaggedDependency),
        default=[],
        metadata=dict(
            description='The flag-specific implementation overrides.'
        ),
    )

    # * method: get_dependency
    def get_dependency(self, *flags) -> FlaggedDependency:
        '''
        Gets a flagged dependency by flag.

        :param flags: The flags to match against flagged dependencies.
        :type flags: Tuple[str, ...]
        :return: The first flagged dependency matching any provided flag, or None.
        :rtype: FlaggedDependency
        '''

        # Return the first dependency that matches any of the provided flags.
        # Input flags are assumed ordinal in priority, so the first match is returned.
        for flag in flags:
            match = next(
                (dependency for dependency in self.dependencies if dependency.flag == flag),
                None
            )
            if match:
                return match

        # Return None if no dependency matches the flags.
        return None
