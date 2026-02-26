"""Tiferet Container Domain Models"""

# *** imports

# ** app
from .settings import (
    DomainObject,
    StringType,
    DictType,
    ListType,
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
        )
    )

    # * attribute: class_name
    class_name = StringType(
        required=True,
        metadata=dict(
            description='The class name.'
        )
    )

    # * attribute: flag
    flag = StringType(
        required=True,
        metadata=dict(
            description='The flag for the container dependency.'
        )
    )

    # * attribute: parameters
    parameters = DictType(
        StringType,
        default={},
        metadata=dict(
            description='The container dependency parameters.'
        )
    )

# ** model: container_attribute
class ContainerAttribute(DomainObject):
    '''
    An attribute that defines container injectior behavior.
    '''

    # * attribute: id
    id = StringType(
        required=True,
        metadata=dict(
            description='The unique identifier for the container attribute.'
        )
    )

    # * attribute: name
    name = StringType(
        metadata=dict(
            description='The name of the container attribute.'
        )
    )

    # * attribute: module_path
    module_path = StringType(
        metadata=dict(
            description='The non-flagged module path for the container attribute.'
        )
    )

    # * attribute: class_name
    class_name = StringType(
        metadata=dict(
            description='The non-flagged class name for the container attribute.'
        )
    )

    # * attribute: parameters
    parameters = DictType(
        StringType,
        default={},
        metadata=dict(
            description='The container attribute parameters.'
        )
    )

    # * attribute: dependencies
    dependencies = ListType(
        ModelType(FlaggedDependency),
        default=[],
        metadata=dict(
            description='The container attribute dependencies.'
        )
    )

    # * method: get_dependency
    def get_dependency(self, *flags) -> FlaggedDependency:
        '''
        Gets a flagged container dependency by flag.

        :param flags: The flags for the flagged container dependency.
        :type flags: Tuple[str, ...]
        :return: The flagged container dependency that matches the first provided flag.
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

