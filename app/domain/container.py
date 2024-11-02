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
    flag = t.StringType(
        required=True,
        metadata=dict(
            description='The flag for the container dependency.'
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
        super(ContainerDependency, ContainerDependency).new(
            ContainerDependency,
            **kwargs)


# ** model: container_attribute
class ContainerAttribute(Entity):
    '''
    A container attribute object.
    '''

    # * attribute: id
    id = t.StringType(
        required=True,
        metadata=dict(
            description='The unique identifier for the container attribute.'
        )
    )

    # * attribute: type
    type = t.StringType(
        required=True,
        choices=CONTAINER_ATTRIBUTE_TYPE_CHOICES,
        metadata=dict(
            description='The type of container attribute.'
        )
    )

    # * attribute: dependencies
    dependencies = t.ListType(
        t.ModelType(ContainerDependency),
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
        super(ContainerAttribute, ContainerAttribute).new(
            ContainerAttribute,
            **kwargs)
