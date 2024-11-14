from ..repos.container import ContainerRepository
from ..domain.container import ContainerAttribute, ContainerDependency
from ..services import container as container_service


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
        attribute: ContainerAttribute = self.container_repo.get_attribute(attribute_id, type)

        # If not attribute is found, create a new one.
        if not attribute:
            attribute = ContainerAttribute.new(
                id=attribute_id,
                type=type,
                dependencies=[ContainerDependency.new(**kwargs)])
        
        # Otherwise, create the container depenedency and add it to the attribute.
        else:
            dependency = ContainerDependency.new(**kwargs)
            attribute.set_dependency(dependency)

        # Save the container attribute.
        self.container_repo.save_attribute(attribute=attribute)

        # Return the new container attribute.
        return attribute
