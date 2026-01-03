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
from ..commands import ImportDependency

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

    # * method: set_default_type
    def set_default_type(
        self,
        module_path=None,
        class_name=None,
        parameters=None,
    ):
        '''
        Update the default type and parameters for this container attribute.

        :param module_path: New module path (or None to clear).
        :type module_path: Optional[str]
        :param class_name: New class name (or None to clear).
        :type class_name: Optional[str]
        :param parameters: New parameters dict (or None to clear all).
        :type parameters: Optional[Dict[str, Any]]
        '''

        # If both type fields are None, clear default type.
        if module_path is None and class_name is None:
            self.module_path = None
            self.class_name = None
            self.parameters = {}
            
        # Otherwise, set them to whatever is provided.
        else:
            self.module_path = module_path
            self.class_name = class_name

        # Update parameters: if parameters is None, clear all; otherwise replace.
        if parameters is None:
            self.parameters = {}
        else:
            self.parameters = {k: v for k, v in parameters.items() if v != None}

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

    # * method: set_dependency
    def set_dependency(self, dependency: FlaggedDependency):
        '''
        Sets a flagged container dependency.

        :param dependency: The flagged container dependency to set.
        :type dependency: ContainerDependency
        '''

        # Replace the value of the dependency if a dependency with the same flag exists.
        for index, dep in enumerate(self.dependencies):
            if dep.flag == dependency.flag:
                self.dependencies[index] = dependency
                return

        # Append the dependency otherwise.
        self.dependencies.append(dependency)