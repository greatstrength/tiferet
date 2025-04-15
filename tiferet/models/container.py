# *** imports

# ** app
from .settings import *


# *** models

# ** model: container_depenedency
class ContainerDependency(ValueObject):
    '''
    A container dependency object.
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
class ContainerAttribute(Entity):
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

    # * attribute: type
    type = StringType(
        required=True,
        choices=CONTAINER_ATTRIBUTE_TYPE_CHOICES,
        metadata=dict(
            description='The type of container attribute.'
        )
    )

    # * attribute: dependencies
    dependencies = ListType(
        ModelType(ContainerDependency),
        default=[],
        metadata=dict(
            description='The container attribute dependencies.'
        )
    )
        
    # * method: get_dependency
    def get_dependency(self, flag: str) -> ContainerDependency:
        '''
        Gets a container dependency by flag.

        :param flag: The flag for the container dependency.
        :type flag: str
        :return: The container dependency.
        :rtype: ContainerDependency
        '''

        # Return the dependency with the matching flag.
        return next(
            (dependency for dependency in self.dependencies if dependency.flag == flag),
            None
        )
        
    # * method: set_dependency
    def set_dependency(self, dependency: ContainerDependency):
        '''
        Sets a container dependency.

        :param dependency: The container dependency to set.
        :type dependency: ContainerDependency
        '''

        # Replace the value of the dependency if a dependency with the same flag exists.
        for index, _dependency in enumerate(self.dependencies):
            if _dependency.flag == dependency.flag:
                self.dependencies[index] = dependency
                return
        
        # Append the dependency otherwise.
        self.dependencies.append(dependency)
