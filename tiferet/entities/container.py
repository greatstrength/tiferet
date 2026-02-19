"""Tiferet Container Models"""

# *** imports

# ** app
from .settings import (
    ModelObject,
    StringType,
    DictType,
    ListType,
    ModelType,
)
from ..events import ImportDependency

# *** models

# ** model: flagged_dependency
class FlaggedDependency(ModelObject):
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
class ContainerAttribute(ModelObject):
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

    # * method: get_type
    def get_type(self, *flags) -> type:
        '''
        Gets the type of the container attribute based on the provided flags.

        :param flags: The flags for the flagged container dependency.
        :type flags: Tuple[str, ...]
        :return: The type of the container attribute.
        :rtype: type
        '''

        # Check the flagged dependencies for the type first.
        for flag in flags:
            dependency = self.get_dependency(flag)
            if dependency:
                return ImportDependency.execute(
                    dependency.module_path,
                    dependency.class_name
                ) 
        
        # Otherwise defer to an available default type.
        if self.module_path and self.class_name:
            return ImportDependency.execute(
                self.module_path,
                self.class_name
            )
        
        # Return None if no type is found.
        return None
