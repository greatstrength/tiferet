from ..repositories.container import ContainerRepository
from ..objects.container import ContainerAttribute
from ..services import container as container_service


class AddContainerAttribute(object):
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

    def execute(self, **kwargs):
        '''
        Execute the command to set a new container attribute.

        :param kwargs: The keyword arguments.
        :type kwargs: dict
        '''

        # Create a new container attribute.
        attribute: ContainerAttribute = container_service.create_attribute(**kwargs)

        # Assert that the attribute does not already exist.
        assert not self.container_repo.attribute_exists(
            **kwargs), f'CONTAINER_ATTRIBUTE_ALREADY_EXISTS: {attribute.group_id}, {attribute.id}'

        # Save the container attribute.
        self.container_repo.save_attribute(attribute=attribute, **kwargs)
