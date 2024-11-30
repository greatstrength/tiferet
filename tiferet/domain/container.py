# *** imports

# ** app
from ..domain import *

# *** constants

# */ list[str]
CONTAINER_ATTRIBUTE_TYPE_CHOICES = [
    'interface',
    'feature',
    'data'
]


# *** models

# ** model: container_depenedency
class ContainerDependency(ModuleDependency):
    '''
    A container dependency object.
    '''

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

    # * method: new
    @staticmethod
    def new(**kwargs) -> 'ContainerDependency':
        '''
        Initializes a new ContainerDependency object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ContainerDependency object.
        :rtype: ContainerDependency
        '''

        # Create and return a new ContainerDependency object.
        return super(ContainerDependency, ContainerDependency).new(
            ContainerDependency,
            **kwargs)


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

    # * method: new
    @staticmethod
    def new(**kwargs) -> 'ContainerAttribute':
        '''
        Initializes a new ContainerAttribute object.

        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        :return: A new ContainerAttribute object.
        :rtype: ContainerAttribute
        '''

        # Create and return a new ContainerAttribute object.
        return super(ContainerAttribute, ContainerAttribute).new(
            ContainerAttribute,
            **kwargs)
        
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
