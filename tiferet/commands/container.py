# *** imports

# ** app
from ..models.container import (
    ModelObject,
    ContainerAttribute,
    FlaggedDependency
)
from ..contracts.container import (
    ContainerRepository
)


class SetContainerAttribute(object):
    '''
    Command to set a new container attribute
    '''

    container_repo: ContainerRepository

    def __init__(self, container_repo: ContainerRepository):
        '''
        Initialize the command to set a new container attribute.

        :param container_repo: The container repository.
        :type container_repo: ContainerRepository
        '''

        self.container_repo = container_repo

    def execute(self, attribute_id: str, type: str, **kwargs):
        '''
        Execute the command to set a new container attribute.

        :param attribute_id: The attribute id.
        :type attribute_id: str
        :param type: The attribute type.
        :type type: str
        :param kwargs: Additional keyword arguments.
        :type kwargs: dict
        '''

        # Look up the container attribute.
        attribute = self.container_repo.get_attribute(attribute_id, type)

        # If not attribute is found, create a new one.
        if not attribute:
            attribute = ModelObject.new(
                ContainerAttribute,
                id=attribute_id,
                type=type,
                dependencies=[ModelObject.new(
                    FlaggedDependency,
                    **kwargs
                )]
            )
        
        # Otherwise, create the container depenedency and add it to the attribute.
        else:
            dependency = ModelObject.new(
                FlaggedDependency,
                **kwargs
            )
            attribute.set_dependency(dependency)

        # Save the container attribute.
        self.container_repo.save_attribute(attribute=attribute)

        # Return the new container attribute.
        return attribute
